"""Synthetic dataset generator stub for KYC/AML document classifier.

This script is a placeholder that demonstrates structure for generating a synthetic
dataset of ID documents. It writes placeholder images (solid color) for each class
into an output directory.
"""
import argparse
import os
from PIL import Image

CLASSES = ["aadhaar", "pan", "voterid", "dl", "passport"]

def generate(output_dir, per_class=10, size=(512, 320)):
    os.makedirs(output_dir, exist_ok=True)
    for cls in CLASSES:
        cls_dir = os.path.join(output_dir, cls)
        os.makedirs(cls_dir, exist_ok=True)
        for i in range(per_class):
            # deterministic-ish color per class
            c = (abs(hash(cls)) % 256, (abs(hash(cls)) // 3) % 256, 150)
            img = Image.new("RGB", size, color=c)
            img_path = os.path.join(cls_dir, f"{cls}_{i:04d}.png")
            img.save(img_path)
    print(f"Generated {per_class} images per class in {output_dir}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", "-o", default="dataset_generator/output_dataset", help="Output directory")
    p.add_argument("--per-class", "-n", type=int, default=10, help="Images per class")
    args = p.parse_args()
    generate(args.output, per_class=args.per_class)