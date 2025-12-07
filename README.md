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
- A **synthetic dataset generator**
- A **TensorFlow EfficientNetB0 classifier**
- A **FastAPI inference API**
- **Docker** for deployment

---

## 📦 Project Structure
```
kyc-aml-document-classifier/
│
├── dataset_generator/
│   ├── generate_synthetic_data.py
│   ├── templates/
│   │   ├── aadhaar_bg.png          (placeholder)
│   │   ├── pan_bg.png              (placeholder)
│   │   ├── voterid_bg.png          (placeholder)
│   │   ├── dl_bg.png               (placeholder)
│   │   ├── passport_bg.png         (placeholder)
│   │   ├── aadhaar_logo.png        (placeholder)
│   │   ├── pan_logo.png            (placeholder)
│   │   ├── eci_logo.png            (placeholder)
│   │   ├── dl_logo.png             (placeholder)
│   │   └── passport_logo.png       (placeholder)
│   └── output_dataset/             (auto-generated)
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
