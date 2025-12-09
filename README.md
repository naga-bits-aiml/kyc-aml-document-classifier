# kyc-aml-document-classifier
ML model to detect Aadhaar/PAN/VoterID/DL/Passport and wrapped in microservice

# KYC/AML Document Type Classifier Microservice

This microservice is part of a modular KYC/AML Automation Platform.  
Its responsibility is to classify uploaded ID documents into one of five supported categories:

- Aadhaar Card  
- PAN Card  
- Voter ID (EPIC)  
- Driving License  
- Passport  

The service uses:
- **Real datasets** from Roboflow and Hugging Face
- A **TensorFlow EfficientNetB0 classifier**
- A **FastAPI inference API**
- **Docker** for deployment

---

## 📦 Project Structure
```
kyc-aml-document-classifier/
│
├── dataset_generator/
│   ├── download_roboflow_dataset.ipynb
│   ├── extract_passport_dataset.ipynb
│   └── dataset/                    (downloaded datasets)
│       ├── train/
│       │   ├── aadhar/
│       │   ├── driving/
│       │   ├── pan/
│       │   ├── voter/
│       │   └── passport/
│       └── valid/
│           ├── aadhar/
│           ├── driving/
│           ├── pan/
│           ├── voter/
│           └── passport/
│
├── training/
│   ├── train_classifier.py
│   ├── augmentations.py
│   └── model/
│       └── (model saved here as efficientnet_model.h5)
│
├── inference/
│   ├── inference_engine.py
│   └── preprocess.py
│
├── api/
│   └── main.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

# How to run locally (quickstart):

## Create & activate a venv:

### Using Python venv:
```
    python3.10 -m venv .venv  # Use Python 3.10
    source .venv/bin/activate  # On Linux/Mac
    .venv\Scripts\Activate.ps1  # On Windows PowerShell
```

### Using Conda (recommended):
```
    conda create -n kyc-aml-env python=3.10 -y
    conda activate kyc-aml-env
```
## Install dependencies:
```
    pip install -r requirements.txt
```

## Download Dataset:

### Step 1: Download Roboflow Dataset (4 classes: aadhar, driving, pan, voter)
1. Download dataset from [Roboflow ID Cards Classification](https://universe.roboflow.com/trial-b8awm/id-cards-classification-phz4u/dataset/1)
2. Extract using the notebook: `dataset_generator/download_roboflow_dataset.ipynb`

### Step 2: Download Passport Dataset from Hugging Face
1. Clone/download passport dataset (Arrow format)
2. Extract using the notebook: `dataset_generator/extract_passport_dataset.ipynb`

Both notebooks will organize the data into `dataset_generator/dataset/` with train/valid splits.

## Train the Model:
```
    python training/train_classifier.py --data dataset_generator/dataset/train --epochs 20
```
## Run API:
```
    uvicorn api.main:app --reload --port 8000
```
