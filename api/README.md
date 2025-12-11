# KYC/AML Document Classifier - API

FastAPI-based REST API for classifying KYC/AML identity documents.

## Quick Start

### 1. Install Dependencies

```bash
# Using conda (recommended)
conda activate kyc-aml-env
pip install -r requirements.txt

# Or using pip only
pip install -r requirements.txt
```

### 2. Download Models

Models are automatically downloaded on first startup. To download manually:

```bash
python inference/download_models.py
```

### 3. Start the API

```bash
# Development
uvicorn api.main:app --reload --port 8000

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root
```
GET /
```
Get API information and available endpoints.

### Health Check
```
GET /health
```
Check if the service is healthy and model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Model Info
```
GET /info
```
Get detailed model information.

**Response:**
```json
{
  "app": "KYC/AML Document Classifier",
  "version": "1.0.0",
  "model": {
    "classes": ["aadhar", "driving", "pan", "passport", "voter"],
    "num_classes": 5,
    "confidence_threshold": 0.5,
    "card_detection_enabled": true,
    "device": "cpu"
  }
}
```

### Get Classes
```
GET /classes
```
Get list of supported document classes.

**Response:**
```json
{
  "classes": ["aadhar", "driving", "pan", "passport", "voter"],
  "num_classes": 5
}
```

### Predict Document Class
```
POST /predict
```
Upload an image and get document classification.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Image file (jpg, jpeg, png, bmp, tiff)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@/path/to/document.jpg"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/predict"
files = {"file": open("document.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "predicted_class": "aadhar",
  "confidence": 0.9823,
  "all_probabilities": {
    "aadhar": 0.9823,
    "driving": 0.0089,
    "pan": 0.0045,
    "passport": 0.0032,
    "voter": 0.0011
  },
  "threshold_met": true,
  "card_detection_used": true,
  "filename": "document.jpg",
  "file_size": 245678
}
```

## Configuration

### Model Configuration (`conf/model_config.json`)
- Model download URLs
- Model version
- Model file paths

### App Configuration (`conf/app_config.json`)
- API settings (host, port)
- Model parameters (classes, thresholds)
- Preprocessing options (card detection, image size)
- Logging configuration

## Docker Deployment

### Build Image
```bash
docker build -t kyc-aml-classifier .
```

### Run Container
```bash
docker run -p 8000:80 kyc-aml-classifier
```

### Test
```bash
curl http://localhost:8000/health
```

## Testing

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Get info
curl http://localhost:8000/info

# Predict
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_aadhar.jpg"
```

### Using Python
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Predict
url = "http://localhost:8000/predict"
with open("sample_aadhar.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    result = response.json()
    
    if result["success"]:
        print(f"Document Type: {result['predicted_class']}")
        print(f"Confidence: {result['confidence']:.2%}")
    else:
        print(f"Error: {result['error']}")
```

## Features

✅ **Automatic Model Download** - Downloads models on first startup  
✅ **Card Detection** - Automatically detects and crops ID cards from images  
✅ **5 Document Types** - Aadhar, Driving License, PAN, Passport, Voter ID  
✅ **Confidence Scores** - Returns confidence for all classes  
✅ **CORS Enabled** - Can be called from web browsers  
✅ **Health Checks** - Kubernetes/Docker ready  
✅ **Fast Inference** - EfficientNetB0 for speed and accuracy  
✅ **GPU Support** - Automatically uses GPU if available  

## Performance

- **Inference Time**: ~50-100ms per image (CPU)
- **Inference Time**: ~10-20ms per image (GPU)
- **Model Size**: ~17MB (EfficientNetB0)
- **Memory Usage**: ~500MB (with model loaded)

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid file type)
- `500` - Internal server error (prediction failed)
- `503` - Service unavailable (model not loaded)

## Environment Variables

```bash
# Optional: Override default port
export PORT=8000

# Optional: Enable debug mode
export DEBUG=true
```

## Monitoring

### Logs
The application logs to stdout. In production, configure a log aggregation service.

### Metrics
Consider adding Prometheus metrics for:
- Request count
- Inference latency
- Model accuracy
- Error rates

## Troubleshooting

### Model not loading
```bash
# Manually download models
python inference/download_models.py

# Check model files exist
ls -la training/model/
```

### CUDA out of memory
Reduce batch size or disable GPU:
```python
# In inference_engine.py, force CPU
self.device = torch.device('cpu')
```

### Slow inference
- Enable GPU if available
- Disable card detection in `conf/app_config.json`
- Use smaller images

## Development

### Project Structure
```
api/
  main.py              # FastAPI application
inference/
  inference_engine.py  # Model inference logic
  download_models.py   # Model downloader
  preprocess.py        # Image preprocessing
conf/
  app_config.json      # Application config
  model_config.json    # Model URLs and paths
training/
  model/               # Trained model files
```

### Adding New Endpoints
Edit `api/main.py` and add new routes following FastAPI conventions.

### Updating Model
1. Train new model
2. Upload to GCS using `upload_model_to_gcs.ipynb`
3. Update URLs in `conf/model_config.json`
4. Restart application

## License

See LICENSE file in repository root.
