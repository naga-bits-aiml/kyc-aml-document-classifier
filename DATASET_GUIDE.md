# Dataset Options for KYC/AML Document Classifier

## Option 1: Download Real Dataset from Roboflow (RECOMMENDED)

This dataset contains **5,586 real images** of ID cards with proper labels.

### Steps:

1. **Create a Roboflow Account** (Free)
   - Visit: https://roboflow.com
   - Sign up for a free account

2. **Get Your API Key**
   - Go to: https://app.roboflow.com/settings/api
   - Copy your private API key

3. **Download the Dataset**
   ```bash
   # Using the Roboflow library (recommended)
   python dataset_generator/download_roboflow_dataset.py --api-key YOUR_API_KEY --use-library --organize
   
   # Or using direct download
   python dataset_generator/download_roboflow_dataset.py --api-key YOUR_API_KEY --organize
   ```

4. **Dataset Info**
   - **Total Images**: 5,586
   - **Train Set**: 5,386 images (96%)
   - **Validation Set**: 200 images (4%)
   - **Classes**: Aadhaar, PAN, Voter ID, Driving License, Passport
   - **Preprocessing**: Auto-orient, resized to 640x640
   - **Augmentations**: Rotation, brightness, blur, noise

### Dataset URL
https://universe.roboflow.com/trial-b8awm/id-cards-classification-phz4u/dataset/1

---

## Option 2: Generate Synthetic Dataset

For testing or when you don't have access to Roboflow, you can generate synthetic documents.

### Generate Synthetic Data
```bash
# Generate 100 images per class (500 total)
python dataset_generator/generate_synthetic_data.py -n 100

# Generate 500 images per class (2500 total)
python dataset_generator/generate_synthetic_data.py -n 500 -o dataset_generator/synthetic_dataset
```

### Features of Synthetic Data:
- ✅ Realistic document layouts
- ✅ Security patterns (guilloche, microtext)
- ✅ QR codes and watermarks
- ✅ Random augmentations
- ✅ Document-specific formatting
- ⚠️ Not as realistic as real photographs

---

## Dataset Structure

After downloading or generating, your dataset should have this structure:

```
dataset_generator/
├── output_dataset/          # Synthetic dataset
│   ├── aadhaar/
│   ├── pan/
│   ├── voterid/
│   ├── dl/
│   └── passport/
│
└── roboflow_dataset/        # Real dataset from Roboflow
    ├── train/
    │   ├── aadhaar/
    │   ├── pan/
    │   ├── voterid/
    │   ├── dl/
    │   └── passport/
    └── valid/
        ├── aadhaar/
        ├── pan/
        ├── voterid/
        ├── dl/
        └── passport/
```

---

## Training the Model

Once you have the dataset, train the model:

```bash
# Train with Roboflow dataset
python training/train_classifier.py --data dataset_generator/roboflow_dataset/train --epochs 20

# Train with synthetic dataset
python training/train_classifier.py --data dataset_generator/output_dataset --epochs 10
```

---

## Comparison

| Feature | Real Dataset (Roboflow) | Synthetic Dataset |
|---------|------------------------|-------------------|
| Number of Images | 5,586 | User-defined (100-1000+) |
| Realism | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Variety | High | Medium |
| Setup Time | 5 minutes | Instant |
| Cost | Free | Free |
| Privacy | Public dataset | Generated |
| Best For | Production models | Quick prototyping |

---

## Recommendations

1. **For Production**: Use the Roboflow dataset for best results
2. **For Testing**: Start with synthetic data to verify your pipeline
3. **Combined Approach**: Use both datasets for data augmentation
4. **Custom Data**: Eventually collect your own real documents for specific use cases
