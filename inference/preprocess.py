"""
Preprocessing module for KYC/AML Document Classifier inference.
Matches the training pipeline from train_classifier.ipynb.

Usage:
    from inference.preprocess import IDCardPreprocessor
    
    preprocessor = IDCardPreprocessor(img_size=380)
    tensor = preprocessor.preprocess("path/to/image.jpg")
    # tensor shape: (1, 3, 380, 380) - ready for model inference
"""

import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms


# ============================================================================
# CONFIGURATION CONSTANTS (must match training)
# ============================================================================
DEFAULT_IMG_SIZE = 380  # Matches training: IMG_SIZE = 380
DEFAULT_ENABLE_DETECTION = True  # Matches training: ENABLE_CARD_DETECTION = True
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


# ============================================================================
# ASPECT PRESERVING RESIZE
# ============================================================================
class AspectPreservingResize:
    """
    Resize image to fit within target size while preserving aspect ratio.
    Pads the remaining space with a fill color (default: black).
    """
    def __init__(self, size, fill_color=(0, 0, 0)):
        self.size = size if isinstance(size, tuple) else (size, size)
        self.fill_color = fill_color

    def __call__(self, img):
        orig_w, orig_h = img.size
        target_w, target_h = self.size
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        new_img = Image.new('RGB', self.size, self.fill_color)
        paste_x, paste_y = (target_w - new_w) // 2, (target_h - new_h) // 2
        new_img.paste(img_resized, (paste_x, paste_y))
        return new_img


# ============================================================================
# ENHANCED CARD DETECTOR (Multi-Strategy)
# ============================================================================
class EnhancedCardDetector:
    """
    Enhanced ID card detector using multiple detection strategies:
    1. Adaptive edge detection with morphological operations
    2. Color-based segmentation (for cards with distinct colors)
    3. Multi-scale Edge Detection (Optimized)
    4. Contour analysis with rectangularity scoring
    """
    
    CARD_ASPECT_RATIOS = {
        'standard': 1.586,  # ISO/IEC 7810 ID-1
        'aadhaar': 1.586,
        'pan': 1.586,
        'driving': 1.586,
        'passport': 0.714,  # Passport photo page
        'voter': 1.586,
    }
    ASPECT_TOLERANCE = 0.4

    def __init__(self, min_area_ratio=0.08, max_area_ratio=0.95, padding=0.03):
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio
        self.padding = padding

    def detect(self, img, visualize=False):
        """Main detection method - tries multiple strategies and picks best result."""
        if isinstance(img, str):
            img = cv2.imread(img)
            if img is None:
                return None, None, "failed"

        orig = img.copy()
        img_h, img_w = img.shape[:2]
        img_area = img_h * img_w

        strategies = [
            ('adaptive_edge', self._detect_adaptive_edge),
            ('color_segmentation', self._detect_color_segmentation),
            ('multi_scale_edge', self._detect_multi_scale_edge),
            ('contour_approx', self._detect_contour_approximation),
        ]

        best_bbox, best_score, best_method = None, 0, "none"

        for method_name, method_func in strategies:
            try:
                bbox = method_func(img)
                if bbox is not None:
                    score = self._score_detection(bbox, img_area)
                    if score > best_score:
                        best_score, best_bbox, best_method = score, bbox, method_name
            except Exception:
                continue

        if best_bbox is not None:
            best_bbox = self._add_padding(best_bbox, img_w, img_h)

        if visualize:
            vis_img = orig.copy()
            if best_bbox is not None:
                x, y, w, h = best_bbox
                cv2.rectangle(vis_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(vis_img, f"{best_method}", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            return best_bbox, vis_img, best_method

        return best_bbox, orig, best_method

    def _detect_adaptive_edge(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.bilateralFilter(enhanced, 9, 75, 75)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return self._find_best_card_contour(contours, img.shape)

    def _detect_color_segmentation(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        masks = [
            cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 50, 255])),      # White
            cv2.inRange(hsv, np.array([15, 20, 150]), np.array([35, 80, 255])),     # Cream
            cv2.inRange(hsv, np.array([90, 30, 100]), np.array([130, 255, 255]))    # Blue
        ]
        best_bbox, best_score = None, 0
        for mask in masks:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            bbox = self._find_best_card_contour(contours, img.shape)
            if bbox:
                score = self._score_detection(bbox, img.shape[0] * img.shape[1])
                if score > best_score:
                    best_score, best_bbox = score, bbox
        return best_bbox

    def _detect_multi_scale_edge(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        best_bbox, best_score = None, 0
        for blur_size in [5]:
            for canny_low in [40, 80]:
                blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
                edges = cv2.Canny(blurred, canny_low, canny_low * 3)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                closed = cv2.morphologyEx(cv2.dilate(edges, kernel, iterations=2),
                                        cv2.MORPH_CLOSE, kernel, iterations=2)
                contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                bbox = self._find_best_card_contour(contours, img.shape)
                if bbox:
                    score = self._score_detection(bbox, img.shape[0] * img.shape[1])
                    if score > best_score:
                        best_score, best_bbox = score, bbox
        return best_bbox

    def _detect_contour_approximation(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        edges = cv2.Canny(enhanced, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.morphologyEx(cv2.dilate(edges, kernel, iterations=2),
                               cv2.MORPH_CLOSE, kernel, iterations=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_bbox, best_score = None, 0
        img_area = img.shape[0] * img.shape[1]

        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if 4 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(approx)
                area = w * h
                if self.min_area_ratio * img_area < area < self.max_area_ratio * img_area:
                    rect_area = cv2.contourArea(approx)
                    if area > 0 and (rect_area / area) > 0.7:
                        score = self._score_detection((x, y, w, h), img_area) * (rect_area / area)
                        if score > best_score:
                            best_score, best_bbox = score, (x, y, w, h)
        return best_bbox

    def _find_best_card_contour(self, contours, img_shape):
        if not contours:
            return None
        img_h, img_w = img_shape[:2]
        img_area = img_h * img_w
        best_bbox, best_score = None, 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if not (self.min_area_ratio * img_area < area < self.max_area_ratio * img_area):
                continue

            aspect_ratio = w / h if h > 0 else 0
            is_card_like = any(abs(aspect_ratio - r)/r < self.ASPECT_TOLERANCE or
                             abs((1/aspect_ratio) - r)/r < self.ASPECT_TOLERANCE
                             for r in self.CARD_ASPECT_RATIOS.values())

            rectangularity = cv2.contourArea(contour) / area if area > 0 else 0
            score = (0.4 * (area / img_area) + 0.3 * rectangularity + 
                    0.2 * (1 if is_card_like else 0.5) +
                    0.1 * (1 - abs(0.5 - (x + w/2) / img_w)))
            if score > best_score:
                best_score, best_bbox = score, (x, y, w, h)
        return best_bbox

    def _score_detection(self, bbox, img_area):
        if bbox is None:
            return 0
        x, y, w, h = bbox
        area_score = min((w * h / img_area) / 0.5, 1.0)
        aspect_ratio = w / h if h > 0 else 0
        aspect_score = 0
        for expected_ratio in self.CARD_ASPECT_RATIOS.values():
            diff = abs(aspect_ratio - expected_ratio) / expected_ratio
            if diff < self.ASPECT_TOLERANCE:
                aspect_score = max(aspect_score, 1 - diff)
        return 0.6 * area_score + 0.4 * aspect_score

    def _add_padding(self, bbox, img_w, img_h):
        x, y, w, h = bbox
        pad_x, pad_y = int(w * self.padding), int(h * self.padding)
        x, y = max(0, x - pad_x), max(0, y - pad_y)
        w, h = min(img_w - x, w + 2 * pad_x), min(img_h - y, h + 2 * pad_y)
        return (x, y, w, h)


# ============================================================================
# MAIN INFERENCE PREPROCESSOR
# ============================================================================
class IDCardPreprocessor:
    """
    Complete preprocessing pipeline for inference.
    Wraps detection, resizing, and normalization.

    Usage:
        preprocessor = IDCardPreprocessor(img_size=380)
        tensor = preprocessor.preprocess("path/to/image.jpg")
        # tensor shape: (1, 3, 380, 380) - ready for model inference
    """
    def __init__(self, img_size=DEFAULT_IMG_SIZE, enable_detection=DEFAULT_ENABLE_DETECTION):
        self.img_size = img_size
        self.detector = EnhancedCardDetector() if enable_detection else None
        self.enable_detection = enable_detection

        # Define transforms
        self.resize = AspectPreservingResize(img_size, fill_color=(0, 0, 0))
        self.normalize = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])

    def preprocess(self, image):
        """
        Preprocess an image for model inference.
        
        Args:
            image: PIL Image, numpy array (BGR), or path to image file
            
        Returns:
            Tensor of shape (1, 3, img_size, img_size) ready for inference
        """
        # Handle input types
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        elif isinstance(image, Image.Image):
            if image.mode != 'RGB':
                image = image.convert('RGB')

        # 1. Card Detection and Cropping
        if self.enable_detection and self.detector:
            img_np = np.array(image)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            bbox, _, _ = self.detector.detect(img_bgr, visualize=False)
            if bbox is not None:
                x, y, w, h = bbox
                img_bgr = img_bgr[y:y+h, x:x+w]
                image = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

        # 2. Resize preserving aspect ratio
        image = self.resize(image)

        # 3. ToTensor and Normalize
        tensor = self.normalize(image)

        # 4. Add batch dimension (1, 3, H, W)
        return tensor.unsqueeze(0)
    
    def preprocess_batch(self, images):
        """
        Preprocess multiple images.
        
        Args:
            images: List of PIL Images, numpy arrays, or paths
            
        Returns:
            Tensor of shape (N, 3, img_size, img_size)
        """
        tensors = [self.preprocess(img) for img in images]
        return torch.cat(tensors, dim=0)


# ============================================================================
# LEGACY FUNCTIONS (for backward compatibility)
# ============================================================================
def load_and_preprocess_for_pytorch(path, target_size=DEFAULT_IMG_SIZE, 
                                     preserve_aspect=True, detect_card=True):
    """
    Legacy function for backward compatibility.
    Use IDCardPreprocessor for new code.
    """
    preprocessor = IDCardPreprocessor(
        img_size=target_size if isinstance(target_size, int) else target_size[0],
        enable_detection=detect_card
    )
    tensor = preprocessor.preprocess(path)
    return tensor.squeeze(0).numpy()  # Return (C, H, W) numpy array


def load_and_preprocess_image(path, target_size=DEFAULT_IMG_SIZE,
                               preserve_aspect=True, detect_card=True):
    """
    Legacy function for backward compatibility.
    Returns (H, W, C) normalized to [0, 1].
    """
    img = Image.open(path).convert("RGB")
    
    if detect_card:
        detector = EnhancedCardDetector()
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        bbox, _, _ = detector.detect(img_bgr, visualize=False)
        if bbox is not None:
            x, y, w, h = bbox
            img_bgr = img_bgr[y:y+h, x:x+w]
            img = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    
    size = target_size if isinstance(target_size, int) else target_size[0]
    if preserve_aspect:
        resize = AspectPreservingResize(size)
        img = resize(img)
    else:
        img = img.resize((size, size))
    
    return np.array(img).astype('float32') / 255.0


# Global preprocessor instance for convenience
_default_preprocessor = None

def get_preprocessor(img_size=DEFAULT_IMG_SIZE, enable_detection=DEFAULT_ENABLE_DETECTION):
    """Get or create a default preprocessor instance."""
    global _default_preprocessor
    if _default_preprocessor is None:
        _default_preprocessor = IDCardPreprocessor(img_size, enable_detection)
    return _default_preprocessor