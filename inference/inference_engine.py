"""
Inference engine for KYC/AML Document Classifier.

Loads PyTorch EfficientNet model and performs document classification.
"""

import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import cv2


# Get project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


class EfficientNetClassifier(nn.Module):
    """EfficientNetB0 based classifier - MUST match training architecture"""
    def __init__(self, num_classes=5):
        super(EfficientNetClassifier, self).__init__()
        # Use base_model attribute to match training checkpoint
        self.base_model = models.efficientnet_b0(weights=None)
        num_features = self.base_model.classifier[1].in_features
        
        # Replace classifier with exact training architecture
        self.base_model.classifier = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(num_features, 256),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(256),
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.base_model(x)


class InferenceEngine:
    """Inference engine for document classification"""
    
    def __init__(self, model_path: Optional[str] = None, config_path: str = "conf/model_config.json"):
        """
        Initialize inference engine.
        
        Args:
            model_path: Path to model file (if None, loads from config)
            config_path: Path to model configuration
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Load configurations
        self._load_configs(config_path)
        
        # Determine model path
        if model_path is None:
            model_dir = PROJECT_ROOT / self.model_config.get('model_path', 'training/model')
            model_path = model_dir / 'efficientnet_model.pth'
        else:
            model_path = PROJECT_ROOT / model_path
        
        self.model_path = model_path
        
        # Load model and class indices
        self._load_model()
        self._load_class_indices()
        
        # Setup preprocessing
        self._setup_transforms()
        
        print(f"✅ Inference engine ready!")
        print(f"   Classes: {self.class_names}")
        print(f"   Device: {self.device}")
    
    def _load_configs(self, config_path: str):
        """Load model and app configurations"""
        # Load model config
        model_config_path = PROJECT_ROOT / config_path
        with open(model_config_path, 'r') as f:
            self.model_config = json.load(f)
        
        # Load app config
        app_config_path = PROJECT_ROOT / "conf" / "app_config.json"
        with open(app_config_path, 'r') as f:
            self.app_config = json.load(f)
        
        self.enable_card_detection = self.app_config['preprocessing']['enable_card_detection']
        self.confidence_threshold = self.app_config['model']['confidence_threshold']
    
    def _load_model(self):
        """Load PyTorch model"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}\n"
                f"Please run: python inference/download_models.py"
            )
        
        print(f"Loading model from: {self.model_path}")
        
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Get number of classes from checkpoint
        num_classes = checkpoint.get('num_classes', 5)
        
        # Initialize model
        self.model = EfficientNetClassifier(num_classes=num_classes)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Model loaded successfully")
    
    def _load_class_indices(self):
        """Load class name mappings"""
        model_dir = self.model_path.parent
        class_indices_path = model_dir / 'class_indices.json'
        
        if class_indices_path.exists():
            with open(class_indices_path, 'r') as f:
                class_info = json.load(f)
                self.class_names = class_info['class_names']
                self.idx_to_class = {i: name for i, name in enumerate(self.class_names)}
        else:
            # Fallback to app config
            self.class_names = self.app_config['model']['class_names']
            self.idx_to_class = {i: name for i, name in enumerate(self.class_names)}
            print(f"⚠️  class_indices.json not found, using default classes")
    
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def detect_and_crop_card(self, image_path: str) -> Image.Image:
        """
        Detect card contour and crop the card region.
        
        Args:
            image_path: Path to input image
        
        Returns:
            Cropped PIL Image
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Combine Canny edges with adaptive threshold
        edges = cv2.Canny(blurred, 30, 100)
        combined = cv2.bitwise_or(edges, cv2.bitwise_not(adaptive_thresh))
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        dilated = cv2.dilate(combined, kernel, iterations=3)
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Evaluate top contours
        best_contour = None
        best_score = 0
        
        for contour in contours[:5]:
            rect = cv2.minAreaRect(contour)
            width, height = rect[1]
            
            if width == 0 or height == 0:
                continue
            
            # Aspect ratio scoring
            aspect_ratio = max(width, height) / min(width, height)
            if 1.2 <= aspect_ratio <= 2.0:
                aspect_ratio_score = 1.0
            elif 1.0 <= aspect_ratio <= 2.5:
                aspect_ratio_score = 0.7
            else:
                aspect_ratio_score = 0.3
            
            # Rectangularity
            contour_area = cv2.contourArea(contour)
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            
            if hull_area > 0:
                rectangularity = contour_area / hull_area
            else:
                rectangularity = 0
            
            score = (aspect_ratio_score * 0.6) + (rectangularity * 0.4)
            
            if score > best_score and score > 0.4:
                best_score = score
                best_contour = rect
        
        # Crop the card region
        if best_contour is not None:
            box = cv2.boxPoints(best_contour)
            box = np.array(box, dtype=np.intp)
            
            x, y, w, h = cv2.boundingRect(box)
            
            # Add padding
            padding_x = int(w * 0.08)
            padding_y = int(h * 0.08)
            
            x = max(0, x - padding_x)
            y = max(0, y - padding_y)
            w = min(image.shape[1] - x, w + 2 * padding_x)
            h = min(image.shape[0] - y, h + 2 * padding_y)
            
            cropped = image[y:y+h, x:x+w]
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            return Image.fromarray(cropped_rgb)
        else:
            # Return original if no card detected
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return Image.fromarray(image_rgb)
    
    def predict(self, image_path: str) -> Dict:
        """
        Predict document class from image.
        
        Args:
            image_path: Path to input image
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Load and preprocess image
            if self.enable_card_detection:
                image = self.detect_and_crop_card(image_path)
            else:
                image = Image.open(image_path).convert('RGB')
            
            # Apply transforms
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
                
                predicted_idx = predicted_idx.item()
                confidence = confidence.item()
            
            # Get class name
            predicted_class = self.idx_to_class.get(predicted_idx, f"class_{predicted_idx}")
            
            # Get all class probabilities
            all_probs = probabilities[0].cpu().numpy()
            class_probabilities = {
                self.idx_to_class[i]: float(prob) 
                for i, prob in enumerate(all_probs)
            }
            
            return {
                "success": True,
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "all_probabilities": class_probabilities,
                "threshold_met": confidence >= self.confidence_threshold,
                "card_detection_used": self.enable_card_detection
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "predicted_class": None,
                "confidence": 0.0
            }
