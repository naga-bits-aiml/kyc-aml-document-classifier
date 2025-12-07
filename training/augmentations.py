"""Image augmentation helpers (stubs).

You can fill these with albumentations or tf.image transforms as needed.
"""
import numpy as np

def random_flip(image):
    # image: numpy array
    if np.random.rand() > 0.5:
        return np.fliplr(image)
    return image

def random_brightness(image, max_delta=0.1):
    return np.clip(image + (np.random.rand() * 2 - 1) * max_delta, 0, 1)