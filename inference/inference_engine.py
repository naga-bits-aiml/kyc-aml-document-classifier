"""
Inference engine for KYC/AML Document Classifier.

Loads PyTorch EfficientNet model and performs document classification.
"""

import json
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, Optional

# Import the preprocessing module (matches training pipeline)
from inference.preprocess import IDCardPreprocessor, DEFAULT_IMG_SIZE


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
        """Setup image preprocessing - uses IDCardPreprocessor to match training"""
        # Use the same preprocessing as training (380x380, aspect preserving, card detection)
        self.preprocessor = IDCardPreprocessor(
            img_size=DEFAULT_IMG_SIZE,  # 380
            enable_detection=self.enable_card_detection
        )
        print(f"   Preprocessing: {DEFAULT_IMG_SIZE}x{DEFAULT_IMG_SIZE}, "
              f"card_detection={self.enable_card_detection}")
    
    def predict(self, image_path: str) -> Dict:
        """
        Predict document class from image.
        
        Args:
            image_path: Path to input image
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Preprocess image using IDCardPreprocessor (matches training pipeline)
            # Returns tensor of shape (1, 3, 380, 380)
            image_tensor = self.preprocessor.preprocess(image_path).to(self.device)
            
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
                "card_detection_used": self.enable_card_detection,
                "preprocessing": {
                    "img_size": DEFAULT_IMG_SIZE,
                    "aspect_preserved": True,
                    "card_detection": self.enable_card_detection
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "predicted_class": None,
                "confidence": 0.0
            }
