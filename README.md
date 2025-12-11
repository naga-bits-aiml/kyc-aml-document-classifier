# KYC/AML Document Classifier

AI-powered microservice for classifying Indian identity documents using deep learning.

## 🎯 Overview

This microservice is part of a modular KYC/AML Automation Platform that classifies uploaded identity documents into one of five supported categories:

- **Aadhar Card** - India's biometric identity document
- **PAN Card** - Permanent Account Number for taxation
- **Voter ID (EPIC)** - Electoral Photo Identity Card
- **Driving License** - Vehicle operation permit
- **Passport** - International travel document

**Key Features:**
- ✅ FastAPI-based REST API
- ✅ EfficientNet-B0 deep learning model
- ✅ Automatic model download from Google Cloud Storage
- ✅ AI agent discovery support (OpenAPI, Plugin manifest)
- ✅ Docker-ready deployment
- ✅ Comprehensive test suite (37 tests, 100% pass rate)
- ✅ Interactive API documentation (Swagger UI)

---

## 📦 Project Structure

```
kyc-aml-document-classifier/
│
├── api/                           # FastAPI application
│   ├── main.py                    # API endpoints with agent discovery
│   └── README.md
│
├── inference/                     # Model inference engine
│   ├── inference_engine.py        # EfficientNet model wrapper
│   ├── preprocess.py              # Image preprocessing
│   └── download_models.py         # Auto-download from GCS
│
├── training/                      # Pre-trained model files
│   ├── efficientnet_model.pth     # PyTorch model (downloaded from GCS)
│   ├── class_indices.json         # Class mappings
│   ├── train_classifier.ipynb     # Training notebook
│   └── upload_model_to_gcs.ipynb  # Model upload notebook
│
├── dataset_generator/             # Dataset management (private)
│   ├── download_roboflow_dataset.ipynb  # Download from Roboflow
│   ├── extract_passport_dataset.ipynb   # Extract passport data
│   ├── upload_to_gcs.ipynb             # Upload to GCS bucket
│   └── dataset/                        # Local dataset (not in repo)
│
├── tests/                         # Comprehensive test suite
│   ├── test_endpoints.py          # 32 endpoint tests
│   ├── test_integration.py        # 3 integration tests
│   ├── run_tests.py               # Test runner with reports
│   └── conftest.py                # Pytest fixtures
│
├── conf/                          # Configuration files
│   ├── app_config.json            # Application settings
│   ├── model_config.json          # Model and GCS URLs
│   └── logging_config.json        # Logging configuration
│
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Docker Compose setup
├── requirements.txt               # Python dependencies
├── requirements-test.txt          # Test dependencies
├── verify_installation.py         # Installation verification
├── AI_AGENT_GUIDE.md             # Guide for AI agent integration
├── DOCKER_DEPLOYMENT.md          # Docker deployment guide
├── ENVIRONMENT_SETUP.md          # Complete setup instructions
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10** (via Conda or venv)
- **2GB free disk space** (for model files)
- **Internet connection** (for downloading models)

### Option 1: Local Setup (Recommended for Development)

#### Step 1: Setup Environment

**Using Conda (Recommended):**
```bash
# Create environment
conda create -n kyc-aml-env python=3.10 -y
conda activate kyc-aml-env

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Optional: Install test dependencies
pip install --no-cache-dir -r requirements-test.txt
```

**Using Python venv:**
```bash
# Create environment
python3.10 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install --no-cache-dir -r requirements.txt
```

#### Step 2: Download Pre-trained Model

The model is automatically downloaded from Google Cloud Storage on first run:

```bash
# Manual download (optional)
python inference/download_models.py
```

**Model Details:**
- **Source**: Private GCS bucket (signed URLs in `conf/model_config.json`)
- **Architecture**: EfficientNet-B0
- **Size**: ~50MB
- **Files**: `efficientnet_model.pth`, `class_indices.json`

#### Step 3: Verify Installation

```bash
python verify_installation.py
```

Expected output:
```
✓ Python 3.10.x (compatible)
✓ All core dependencies installed
✓ Model files present
✓ Port 8000 available
✓ All checks passed!
```

#### Step 4: Start API Server

```bash
# Development mode (with auto-reload)
python -m uvicorn api.main:app --reload --port 8000

# Production mode
python -m uvicorn api.main:app --port 8000
```

Server will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **AI Plugin**: http://localhost:8000/.well-known/ai-plugin.json

### Option 2: Docker Deployment

#### Quick Deploy with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Manual Docker Build

```bash
# Build image
docker build -t kyc-classifier:latest .

# Run container
docker run -d \
  --name kyc-aml-classifier \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  kyc-classifier:latest
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed Docker instructions.

---

## 📖 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-12-11T10:30:00.000000"
}
```

### Get Supported Classes

```bash
curl http://localhost:8000/classes
```

Response:
```json
{
  "classes": ["aadhar", "driving", "pan", "passport", "voter"],
  "num_classes": 5,
  "descriptions": {
    "aadhar": "Aadhar Card - India's biometric identity document",
    "driving": "Driving License - Vehicle operation permit",
    "pan": "PAN Card - Permanent Account Number for taxation",
    "passport": "Passport - International travel document",
    "voter": "Voter ID - Electoral identity card"
  }
}
```

### Classify Document

**Using curl:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.jpg"
```

**Using Python:**
```python
import requests

with open('document.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    )

result = response.json()
print(f"Document Type: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.2%}")
```

Response:
```json
{
  "success": true,
  "predicted_class": "passport",
  "confidence": 0.9856,
  "probabilities": {
    "aadhar": 0.0012,
    "driving": 0.0045,
    "pan": 0.0031,
    "passport": 0.9856,
    "voter": 0.0056
  },
  "filename": "document.jpg",
  "file_size": 245678
}
```

---

## 🤖 AI Agent Integration

This API is designed for easy discovery and integration with AI agents (ChatGPT, LangChain, AutoGPT, etc.).

### Agent Discovery Endpoints

- **OpenAPI Spec**: `/openapi.json` - Complete API specification
- **AI Plugin Manifest**: `/.well-known/ai-plugin.json` - Agent-friendly metadata
- **Service Info**: `/info` - Runtime capabilities

### Quick Agent Example

```python
import requests

# Discover service
manifest = requests.get("http://localhost:8000/.well-known/ai-plugin.json").json()
print(f"Service: {manifest['name_for_human']}")
print(f"Description: {manifest['description_for_model']}")

# Use service
with open('id_card.jpg', 'rb') as f:
    result = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    ).json()

print(f"Result: {result['predicted_class']}")
```

See [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md) for comprehensive integration guide with LangChain, OpenAI, and other frameworks.

---

## 🧪 Testing

### Run All Tests

```bash
# Run full test suite with reports
python tests/run_tests.py

# View reports
# - test_reports/test_report_*.html
# - test_reports/coverage/index.html
```

### Quick Test

```bash
# Run tests, stop on first failure
python test_quick.py
```

### Test Coverage

- **Total Tests**: 37
- **Pass Rate**: 100%
- **Code Coverage**: 70% overall
  - `api/main.py`: 86%
  - `inference/inference_engine.py`: 70%

---

## 🎓 Training (Optional)

The service uses a pre-trained model, but you can retrain if needed.

### Dataset Information

- **Source**: Private datasets from Roboflow and Hugging Face
- **Storage**: Google Cloud Storage (private bucket)
- **Access**: Signed URLs in `conf/model_config.json`
- **Classes**: 5 (aadhar, driving, pan, passport, voter)

### Training Workflow

1. **Download Dataset**: Use notebooks in `dataset_generator/`
   - `download_roboflow_dataset.ipynb` - 4 classes from Roboflow
   - `extract_passport_dataset.ipynb` - Passport class from HuggingFace

2. **Upload to GCS** (optional): `upload_to_gcs.ipynb`

3. **Train Model**: `training/train_classifier.ipynb`
   - Architecture: EfficientNet-B0
   - Framework: PyTorch
   - Optimizer: Adam
   - Data Augmentation: Included

4. **Upload Trained Model**: `training/upload_model_to_gcs.ipynb`

**Note**: Dataset is NOT included in the repository due to size and licensing. Use provided notebooks to download from original sources.

---

## 📚 Documentation

- **[AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)** - AI agent integration guide
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Complete setup instructions
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Docker deployment guide
- **[TEST_SUITE_SUMMARY.md](TEST_SUITE_SUMMARY.md)** - Test results and metrics
- **[QUICK_TEST_GUIDE.md](QUICK_TEST_GUIDE.md)** - Quick testing reference
- **Interactive API Docs**: http://localhost:8000/docs

---

## 🛠️ Development

### Project Dependencies

**Core:**
- FastAPI 0.124.2
- Uvicorn 0.38.0
- PyTorch 2.9.1+cpu
- TorchVision 0.24.1+cpu
- OpenCV 4.10.0
- Pillow 12.0.0
- NumPy 2.2.6

**Testing:**
- pytest 9.0.2
- pytest-html 4.1.1
- pytest-cov 7.0.0
- httpx 0.28.1

### Common Commands

```bash
# Start API server
conda activate kyc-aml-env
python -m uvicorn api.main:app --reload --port 8000

# Run tests
python tests/run_tests.py

# Verify installation
python verify_installation.py

# Download models manually
python inference/download_models.py

# Docker build
docker build -t kyc-classifier .
docker-compose up -d
```

---

## 🔧 Configuration

Configuration files in `conf/`:

- **`app_config.json`** - Application settings (API host, port, preprocessing)
- **`model_config.json`** - Model paths and GCS download URLs
- **`logging_config.json`** - Logging configuration

---

## 📊 Model Performance

- **Architecture**: EfficientNet-B0
- **Training Dataset**: ~5000 images across 5 classes
- **Accuracy**: >95% on validation set
- **Inference Time**: <1 second per image (CPU)
- **Device**: CPU (GPU optional)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/run_tests.py`
5. Submit a pull request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/naga-bits-aiml/kyc-aml-document-classifier/issues)
- **Documentation**: http://localhost:8000/docs
- **API Reference**: http://localhost:8000/openapi.json

---

## ✨ Features

- [x] Multi-class document classification (5 classes)
- [x] REST API with FastAPI
- [x] Automatic model download from GCS
- [x] Docker deployment support
- [x] Comprehensive test suite
- [x] AI agent discovery (OpenAPI, Plugin manifest)
- [x] Interactive API documentation
- [x] Health monitoring endpoints
- [x] CORS support
- [x] Logging and error handling

---

**Made with responsibility for KYC/AML automation**
