
# ============================================================
# KYC/AML Identity Classifier - Model Deployment
# ============================================================

# Method 1: Download using Signed URLs (No Authentication Required)
# Valid for 365 days from generation date

import urllib.request
import os

# Create model directory
os.makedirs('model', exist_ok=True)

# Download model files
model_urls = {
    "efficientnet_model.pth": "https://storage.googleapis.com/kyc-aml-model/document_classification/v1/efficientnet_model.pth?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-iac%40kyc-aml-automation.iam.gserviceaccount.com%2F20251210%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251210T230003Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=896163090cd4f3a899c40bb7fc8e9cc5bbbb95da75f09050c951f8cd25dbeac0763d8f0ca578ce38c96e3a3d7cda1ee8c85c0dec26682f378a241f6ce0cc2785032cce4faa16e85c5f7c8a022757bc6170bd27c1ee1e9de6aa0761d8f7b12648492c82cccc7373201095ec5551ec03cfa245714ee16be5d6d73b93535bf4dc33fe9b89b17e1f4ebeb27ee6e048bad19dbdae5ad155054b9dda116e06d280bcd2ef52ba5c599d1bc2647f3279e6e1b4a714a7666cbfba8a25fea99433f1d7cf0e041435b04c03b2cb42a8be24b2a61bb0cf13cc26214ccc79dfeeaa6ac7af39b8fe5bb21e4d3556f9aea7cb34f216429f6a10b1334eb2ebb39178a7320470e2ab",
    "class_indices.json": "https://storage.googleapis.com/kyc-aml-model/document_classification/v1/class_indices.json?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-iac%40kyc-aml-automation.iam.gserviceaccount.com%2F20251210%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251210T230003Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=ae20bfaea41eb57ab272ed95e86711863ebbfd7b95ff183f7986edf707038c709f2071496eee2332789dd423c2f84b51d6d01c3802ff467905e411114c64caf58677a9d32d20c813e16da3ba30999bfddbe2b554349400eed7f337e8a5c3bff04c67f4262025fae5ed868393700fedd15c1f42384c6c2ff3619939a19db41f9fd0e2b8a2d4517bbaaa0953ec78b0b2771bbc04ea419c19ce8bb48d6b04bbb820f2802136f5fe8d9bac82c5202a37e32895285fef15b922a8be40964dc69bd74ce76279bf03796ace502b64c476385e4a9231477826caf38fa1ec8d1650b36965aeb2681342debc0ffaadd2ff4593b0cd1092740ffc8a30fe755ad2a0b5457f12",
    "training_history.json": "https://storage.googleapis.com/kyc-aml-model/document_classification/v1/training_history.json?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-iac%40kyc-aml-automation.iam.gserviceaccount.com%2F20251210%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251210T230003Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=3a08cd9335f2820a91123c3715f7c94f6a05dbc8b657148527094ebc869bdcb371bb723a07fc60c4095aa58a31e013ae7d94e9baa3b79710d01632d892702b69dd91eceddc92073b04cfd0b726c01a49d1eadc64f8f6e796c19b347defff02479b87c3686d034e9453f42d7aaedc572a55bcf71008516e76826495dcb5890048d800bfa4e75120d1ce90838a693d0272e7437e8d6205662662b18d3dd8de2140937ad826859b1871fa64562e476fa4bc5a18ef35ca6a5b2bc2c32d06e129357ca2b8569ed4a9beeb420d83f93e9ada03512c4eadec4b653d454e31857e10018ed781c8a8c0fb51aff643a4e37394edc5d001cf1ff63c5822155a7cf1fa0315d6",
}

for file_name, url in model_urls.items():
    print(f"Downloading {file_name}...")
    urllib.request.urlretrieve(url, f"model/{file_name}")
    print(f"✅ Downloaded {file_name}")

print("
✅ All model files downloaded!")

# ============================================================
# Method 2: Download using GCS API (Requires Authentication)
# ============================================================

from google.cloud import storage
import os

# Set credentials (if not running on GCP)
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account.json'

# Initialize client
client = storage.Client(project='kyc-aml-automation')
bucket = client.bucket('kyc-aml-model')

# Download model files
model_files = ['efficientnet_model.pth', 'class_indices.json', 'training_history.json', 'efficientnet_model.onnx']
gcs_prefix = 'document_classification/v1'

os.makedirs('model', exist_ok=True)

for file_name in model_files:
    blob_path = f"{gcs_prefix}/{file_name}"
    local_path = f"model/{file_name}"
    
    print(f"Downloading {file_name}...")
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)
    print(f"✅ Downloaded {file_name}")

print("
✅ All model files downloaded!")

# ============================================================
# Method 3: Docker Deployment (Download during build)
# ============================================================

# Add to Dockerfile:

# Download models during Docker build
RUN mkdir -p /app/model && \
    wget -O /app/model/efficientnet_model.pth 'https://storage.googleapis.com/kyc-aml-model/document_classification/v1/efficientnet_model.pth?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-iac%40kyc-aml-automation.iam.gserviceaccount.com%2F20251210%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251210T230003Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=896163090cd4f3a899c40bb7fc8e9cc5bbbb95da75f09050c951f8cd25dbeac0763d8f0ca578ce38c96e3a3d7cda1ee8c85c0dec26682f378a241f6ce0cc2785032cce4faa16e85c5f7c8a022757bc6170bd27c1ee1e9de6aa0761d8f7b12648492c82cccc7373201095ec5551ec03cfa245714ee16be5d6d73b93535bf4dc33fe9b89b17e1f4ebeb27ee6e048bad19dbdae5ad155054b9dda116e06d280bcd2ef52ba5c599d1bc2647f3279e6e1b4a714a7666cbfba8a25fea99433f1d7cf0e041435b04c03b2cb42a8be24b2a61bb0cf13cc26214ccc79dfeeaa6ac7af39b8fe5bb21e4d3556f9aea7cb34f216429f6a10b1334eb2ebb39178a7320470e2ab' && \
    wget -O /app/model/class_indices.json 'https://storage.googleapis.com/kyc-aml-model/document_classification/v1/class_indices.json?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-iac%40kyc-aml-automation.iam.gserviceaccount.com%2F20251210%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251210T230003Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=ae20bfaea41eb57ab272ed95e86711863ebbfd7b95ff183f7986edf707038c709f2071496eee2332789dd423c2f84b51d6d01c3802ff467905e411114c64caf58677a9d32d20c813e16da3ba30999bfddbe2b554349400eed7f337e8a5c3bff04c67f4262025fae5ed868393700fedd15c1f42384c6c2ff3619939a19db41f9fd0e2b8a2d4517bbaaa0953ec78b0b2771bbc04ea419c19ce8bb48d6b04bbb820f2802136f5fe8d9bac82c5202a37e32895285fef15b922a8be40964dc69bd74ce76279bf03796ace502b64c476385e4a9231477826caf38fa1ec8d1650b36965aeb2681342debc0ffaadd2ff4593b0cd1092740ffc8a30fe755ad2a0b5457f12' && \
    wget -O /app/model/training_history.json 'https://storage.googleapis.com/kyc-aml-model/document_classification/v1/training_history.json?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-iac%40kyc-aml-automation.iam.gserviceaccount.com%2F20251210%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251210T230003Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=3a08cd9335f2820a91123c3715f7c94f6a05dbc8b657148527094ebc869bdcb371bb723a07fc60c4095aa58a31e013ae7d94e9baa3b79710d01632d892702b69dd91eceddc92073b04cfd0b726c01a49d1eadc64f8f6e796c19b347defff02479b87c3686d034e9453f42d7aaedc572a55bcf71008516e76826495dcb5890048d800bfa4e75120d1ce90838a693d0272e7437e8d6205662662b18d3dd8de2140937ad826859b1871fa64562e476fa4bc5a18ef35ca6a5b2bc2c32d06e129357ca2b8569ed4a9beeb420d83f93e9ada03512c4eadec4b653d454e31857e10018ed781c8a8c0fb51aff643a4e37394edc5d001cf1ff63c5822155a7cf1fa0315d6'

# ============================================================
# Method 4: Load Model in Inference Code
# ============================================================

import torch
import json
from torchvision import models

# Load class indices
with open('model/class_indices.json', 'r') as f:
    class_info = json.load(f)
    class_names = class_info['class_names']

# Load PyTorch model
checkpoint = torch.load('model/efficientnet_model.pth', map_location='cpu')
model = EfficientNetClassifier(num_classes=len(class_names))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(f"✅ Model loaded: {len(class_names)} classes")
print(f"   Classes: {class_names}")
