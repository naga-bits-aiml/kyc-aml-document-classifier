"""Inference engine wrapper.

Loads a model (if available) and exposes a predict(image_path) method that
returns (label, confidence). If model is missing, returns a dummy prediction.
"""
import os
import numpy as np

try:
    import tensorflow as tf
except Exception:
    tf = None

from .preprocess import load_and_preprocess_image

CLASS_MAP = ["aadhaar", "pan", "voterid", "dl", "passport"]

class InferenceEngine:
    def __init__(self, model_path="training/model/efficientnet_model.h5"):
        self.model_path = model_path
        self.model = None
        if tf is not None and os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            print(f"Loaded model from {model_path}")
        else:
            print("Model not found or TensorFlow not available — using dummy predictor")

    def predict(self, image_path):
        img = load_and_preprocess_image(image_path, target_size=(224,224))
        if self.model is None:
            # dummy deterministic prediction based on filename hash
            idx = abs(hash(os.path.basename(image_path))) % len(CLASS_MAP)
            return {"label": CLASS_MAP[idx], "confidence": float(0.5 + (idx / 10))}
        preds = self.model.predict(np.expand_dims(img, axis=0))[0]
        idx = int(np.argmax(preds))
        return {"label": CLASS_MAP[idx], "confidence": float(preds[idx])}