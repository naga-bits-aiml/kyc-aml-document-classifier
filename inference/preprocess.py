"""Preprocessing helpers for inference."""
from PIL import Image
import numpy as np

def load_and_preprocess_image(path, target_size=(224,224)):
    img = Image.open(path).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype('float32') / 255.0
    return arr