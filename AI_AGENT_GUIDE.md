# AI Agent Integration Guide

This guide explains how AI agents can discover and use the KYC/AML Document Classifier API.

## Agent Discovery

The API provides multiple endpoints for automatic service discovery:

### 1. **OpenAPI Specification** (Recommended)
```
GET /openapi.json
```
- **Standard**: OpenAPI 3.0 (Swagger)
- **Content**: Complete API specification with all endpoints, parameters, and schemas
- **Use Case**: Primary method for agent discovery and integration
- **Format**: JSON

### 2. **AI Plugin Manifest**
```
GET /.well-known/ai-plugin.json
```
- **Standard**: OpenAI Plugin Specification
- **Content**: Human and machine-readable service description
- **Use Case**: AI agent frameworks (ChatGPT, LangChain, AutoGPT, etc.)
- **Format**: JSON

### 3. **Service Information**
```
GET /info
```
- **Content**: Detailed API capabilities, model info, supported classes
- **Use Case**: Runtime capability discovery
- **Format**: JSON

## Quick Start for AI Agents

### Step 1: Discover the Service

```python
import requests

# Method 1: Get AI Plugin Manifest
manifest = requests.get("http://localhost:8000/.well-known/ai-plugin.json").json()
print(f"Service: {manifest['name_for_human']}")
print(f"Capabilities: {manifest['capabilities']}")

# Method 2: Get OpenAPI Spec
openapi_spec = requests.get("http://localhost:8000/openapi.json").json()
print(f"API Version: {openapi_spec['info']['version']}")
print(f"Available Endpoints: {list(openapi_spec['paths'].keys())}")

# Method 3: Get Service Info
info = requests.get("http://localhost:8000/info").json()
print(f"Supported Classes: {info['model']['classes']}")
```

### Step 2: Check Service Health

```python
# Verify service is ready
health = requests.get("http://localhost:8000/health").json()
if health['status'] == 'healthy' and health['model_loaded']:
    print("✓ Service ready for predictions")
else:
    print("✗ Service not ready")
```

### Step 3: Make Predictions

```python
# Classify a document
with open('document.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': ('document.jpg', f, 'image/jpeg')}
    )

result = response.json()
print(f"Document Type: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"All Probabilities: {result['probabilities']}")
```

## API Endpoints

### Information Endpoints

#### `GET /`
**Purpose**: Root endpoint with service overview  
**Returns**: Basic info, available endpoints, agent discovery URLs  
**Auth**: None  

#### `GET /health`
**Purpose**: Service health check  
**Returns**: Status, model readiness, timestamp  
**Auth**: None  

#### `GET /info`
**Purpose**: Detailed service capabilities  
**Returns**: Model details, supported formats, endpoints  
**Auth**: None  

#### `GET /classes`
**Purpose**: Get supported document classes  
**Returns**: List of classes with descriptions  
**Auth**: None  

### Prediction Endpoint

#### `POST /predict`
**Purpose**: Classify identity document image  
**Input**: Multipart form-data with image file  
**Output**: Predicted class, confidence, probabilities  
**Auth**: None  
**Supported Formats**: JPEG, PNG, BMP, TIFF  

**Request Example:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.jpg"
```

**Response Example:**
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

### Discovery Endpoints

#### `GET /openapi.json`
**Purpose**: OpenAPI 3.0 specification  
**Returns**: Complete API schema  
**Auth**: None  
**Use**: Import into agent frameworks  

#### `GET /.well-known/ai-plugin.json`
**Purpose**: AI plugin manifest  
**Returns**: Agent-friendly service description  
**Auth**: None  
**Standard**: OpenAI Plugin Spec  

#### `GET /docs`
**Purpose**: Interactive API documentation  
**Returns**: Swagger UI  
**Auth**: None  
**Use**: Human-readable docs  

## Integration Patterns

### Pattern 1: LangChain Integration

```python
from langchain.tools import Tool
import requests

def classify_document(image_path: str) -> str:
    """Classify an Indian identity document."""
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/predict',
            files={'file': f}
        )
    result = response.json()
    return f"Document type: {result['predicted_class']} (confidence: {result['confidence']:.1%})"

document_classifier = Tool(
    name="Indian_Document_Classifier",
    func=classify_document,
    description="Classifies Indian identity documents (Aadhar, PAN, Passport, Driving License, Voter ID) from images. Input should be a file path to the document image."
)
```

### Pattern 2: OpenAI Function Calling

```python
# Define function for OpenAI
functions = [{
    "name": "classify_indian_document",
    "description": "Classifies Indian identity documents from images into categories: Aadhar Card, Driving License, PAN Card, Passport, or Voter ID",
    "parameters": {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the document image file"
            }
        },
        "required": ["image_path"]
    }
}]

# Implement function
def classify_indian_document(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/predict',
            files={'file': f}
        )
    return response.json()
```

### Pattern 3: AutoGPT Plugin

```python
# Plugin manifest for AutoGPT
{
    "name": "KYC-AML-Document-Classifier",
    "version": "1.0.0",
    "description": "Classifies Indian identity documents for KYC/AML verification",
    "api": {
        "base_url": "http://localhost:8000",
        "endpoints": {
            "classify": {
                "method": "POST",
                "path": "/predict",
                "description": "Upload document image for classification"
            }
        }
    }
}
```

## Supported Document Types

| Class | Description | Use Case |
|-------|-------------|----------|
| `aadhar` | Aadhar Card | India's biometric identity document, government-issued unique ID |
| `driving` | Driving License | Vehicle operation permit issued by transport authorities |
| `pan` | PAN Card | Permanent Account Number for taxation and financial transactions |
| `passport` | Passport | International travel document |
| `voter` | Voter ID | Electoral Photo Identity Card for voting |

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful prediction
- `400 Bad Request`: Invalid file format or missing file
- `422 Unprocessable Entity`: Invalid input parameters
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Model not loaded

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Performance Considerations

### Request Limits
- **Max file size**: Check `app_config.json` for limits (typically 10MB)
- **Supported formats**: JPEG, PNG, BMP, TIFF
- **Concurrent requests**: Service can handle multiple concurrent requests

### Latency
- **Typical response time**: < 1 second per image
- **Factors**: Image size, server load, CPU vs GPU

### Best Practices
1. **Check health** before batch processing
2. **Resize large images** before uploading to reduce latency
3. **Handle timeouts** gracefully (set 30s timeout)
4. **Retry logic** for 503 errors (model loading)

## Security Considerations

### Current Configuration
- **Authentication**: None (open API)
- **CORS**: Enabled for all origins
- **Rate Limiting**: Not implemented

### Production Recommendations
1. **Add authentication** (API keys, OAuth2)
2. **Implement rate limiting** to prevent abuse
3. **Configure CORS** for specific origins only
4. **Use HTTPS** for encrypted communication
5. **Add input validation** for file types and sizes
6. **Implement logging** and monitoring

## Example: Complete Agent Workflow

```python
import requests
from typing import Dict, Any

class DocumentClassifierAgent:
    """AI Agent for document classification."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.capabilities = None
        
    def discover(self) -> Dict[str, Any]:
        """Discover service capabilities."""
        manifest = requests.get(f"{self.base_url}/.well-known/ai-plugin.json").json()
        info = requests.get(f"{self.base_url}/info").json()
        
        self.capabilities = {
            "name": manifest["name_for_human"],
            "description": manifest["description_for_human"],
            "supported_classes": info["model"]["classes"],
            "model": info["model"]["architecture"]
        }
        return self.capabilities
    
    def check_health(self) -> bool:
        """Check if service is healthy."""
        try:
            health = requests.get(f"{self.base_url}/health", timeout=5).json()
            return health["status"] == "healthy" and health["model_loaded"]
        except:
            return False
    
    def classify(self, image_path: str) -> Dict[str, Any]:
        """Classify a document image."""
        if not self.check_health():
            raise Exception("Service not healthy")
        
        with open(image_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/predict",
                files={'file': f},
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Classification failed: {response.text}")

# Usage
agent = DocumentClassifierAgent()
agent.discover()
print(f"Connected to: {agent.capabilities['name']}")
print(f"Supported classes: {agent.capabilities['supported_classes']}")

result = agent.classify("passport.jpg")
print(f"Result: {result['predicted_class']} ({result['confidence']:.1%})")
```

## Testing the API

### Using curl
```bash
# Get service info
curl http://localhost:8000/info

# Check health
curl http://localhost:8000/health

# Get classes
curl http://localhost:8000/classes

# Classify document
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.jpg"
```

### Using Python requests
```python
import requests

# Test all endpoints
base_url = "http://localhost:8000"

# Root
root = requests.get(f"{base_url}/").json()
print("Endpoints:", root['endpoints'])

# Health
health = requests.get(f"{base_url}/health").json()
print("Status:", health['status'])

# Info
info = requests.get(f"{base_url}/info").json()
print("Model:", info['model']['architecture'])

# Classes
classes = requests.get(f"{base_url}/classes").json()
print("Supported:", classes['classes'])

# Predict
with open('test_image.jpg', 'rb') as f:
    result = requests.post(f"{base_url}/predict", files={'file': f}).json()
    print("Prediction:", result['predicted_class'])
```

## Additional Resources

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc
- **GitHub**: https://github.com/naga-bits-aiml/kyc-aml-document-classifier
- **Issues**: https://github.com/naga-bits-aiml/kyc-aml-document-classifier/issues

## Support

For questions or issues:
1. Check the interactive documentation at `/docs`
2. Review the OpenAPI specification at `/openapi.json`
3. Open an issue on GitHub
4. Check service health at `/health`
