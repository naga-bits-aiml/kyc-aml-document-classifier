# Environment Setup Guide

This guide provides step-by-step instructions for setting up the development environment for the KYC-AML Document Classifier.

## Prerequisites

- **Anaconda** or **Miniconda** installed
- **Python 3.10** (managed by conda)
- **Git** (for cloning repository)
- At least **2GB free disk space**
- Internet connection for downloading dependencies and models

## Installation Steps

### Step 1: Install Conda (if not already installed)

**Windows:**
1. Download [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download)
2. Run the installer
3. Choose "Add Anaconda/Miniconda to PATH" (or manually add later)
4. Verify installation:
   ```powershell
   conda --version
   ```

**Linux/Mac:**
```bash
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Verify installation
conda --version
```

### Step 2: Clone Repository

```powershell
# Navigate to your projects directory
cd <your-projects-directory>

# Clone the repository
git clone https://github.com/naga-bits-aiml/kyc-aml-document-classifier.git

# Navigate to project directory
cd kyc-aml-document-classifier
```

### Step 3: Remove Existing Environment (if any)

```powershell
# Check existing environments
conda env list

# Remove old environment if exists
conda env remove -n kyc-aml-env

# Confirm removal
conda env list
```

### Step 4: Create New Environment

```powershell
# Create environment with Python 3.10
conda create -n kyc-aml-env python=3.10 -y

# Activate the environment
conda activate kyc-aml-env

# Verify Python version
python --version
# Expected: Python 3.10.x
```

### Step 5: Install Core Dependencies

```powershell
# Install from requirements.txt
pip install --no-cache-dir -r requirements.txt

# This installs:
# - FastAPI & Uvicorn (Web framework)
# - PyTorch & TorchVision (Deep learning)
# - OpenCV & Pillow (Image processing)
# - NumPy (Numerical computing)
# - Requests (HTTP client)
```

### Step 6: Install Test Dependencies (Optional)

```powershell
# Install testing tools
pip install --no-cache-dir -r requirements-test.txt

# This installs:
# - pytest (Testing framework)
# - pytest-html (HTML reports)
# - pytest-cov (Coverage reports)
# - httpx (Async HTTP client for tests)
```

### Step 7: Download ML Models

```powershell
# Download pre-trained models from GCS
python inference/download_models.py

# This downloads:
# - efficientnet_model.pth (~50MB)
# - class_indices.json
# - training_history.json (optional)
```

### Step 8: Verify Installation

```powershell
# Check installed packages
pip list

# Verify key packages
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import PIL; print('Pillow:', PIL.__version__)"

# Check if models exist
ls training/efficientnet_model.pth
ls training/class_indices.json
```

## Running the Application

### Start API Server

```powershell
# Activate environment
conda activate kyc-aml-env

# Start with auto-reload (development)
python -m uvicorn api.main:app --reload --port 8000

# Or start without reload (production-like)
python -m uvicorn api.main:app --port 8000
```

### Access API

- **Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Test the API

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test with sample image
curl -X POST "http://localhost:8000/predict" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@path\to\document.jpg"
```

## Running Tests

```powershell
# Activate environment
conda activate kyc-aml-env

# Quick test (stops on first failure)
python test_quick.py

# Full test suite with reports
python tests/run_tests.py

# Generate custom visualization report
python tests/generate_report.py

# View reports
Start-Process test_reports\test_report_*.html
Start-Process test_reports\coverage\index.html
```

## Troubleshooting

### Issue: Conda command not found

**Solution**: Add Conda to PATH or use Anaconda Prompt

```powershell
# Option 1: Use Anaconda Prompt instead of PowerShell

# Option 2: Add to PATH (restart terminal after)
# Replace <conda-install-path> with your actual conda installation path
$env:Path += ";<conda-install-path>\Scripts"
$env:Path += ";<conda-install-path>\condabin"

# Example:
# $env:Path += ";C:\Users\YourName\anaconda3\Scripts"
# $env:Path += ";C:\Users\YourName\anaconda3\condabin"
```

### Issue: OpenCV import error

**Solution**: Reinstall opencv-python-headless

```powershell
conda activate kyc-aml-env
pip uninstall opencv-python opencv-python-headless -y
pip install --no-cache-dir opencv-python-headless==4.8.0.74
```

### Issue: NumPy compatibility error

**Solution**: Install specific version

```powershell
conda activate kyc-aml-env
pip install --force-reinstall numpy==1.26.4
```

### Issue: PyTorch CPU only

**Solution**: Install PyTorch with CUDA support (if GPU available)

```powershell
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Issue: Model download fails

**Solution**: Manually download or check network

```powershell
# Check network connectivity
Test-Connection storage.googleapis.com

# Retry download
python inference/download_models.py

# Or download manually from URLs in training/model_download_urls.txt
```

### Issue: Port 8000 already in use

**Solution**: Use different port or kill process

```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn api.main:app --port 8001
```

### Issue: Permission denied on logs/

**Solution**: Ensure directory permissions

```powershell
# Create logs directory if missing
New-Item -ItemType Directory -Force -Path logs

# Or run as administrator (not recommended)
```

## Environment Management

### List all environments
```powershell
conda env list
```

### Activate environment
```powershell
conda activate kyc-aml-env
```

### Deactivate environment
```powershell
conda deactivate
```

### Export environment
```powershell
conda activate kyc-aml-env
conda env export > environment.yml
```

### Create from exported environment
```powershell
conda env create -f environment.yml
```

### Update packages
```powershell
conda activate kyc-aml-env
pip install --upgrade -r requirements.txt
```

### Clean conda cache
```powershell
conda clean --all -y
```

## Development Workflow

### 1. Fresh Start (Daily)
```powershell
# Activate environment
conda activate kyc-aml-env

# Start API server
python -m uvicorn api.main:app --reload --port 8000
```

### 2. Make Code Changes
- Edit files in `api/`, `inference/`, or `conf/`
- Server auto-reloads with `--reload` flag

### 3. Test Changes
```powershell
# Quick test
python test_quick.py

# Full test suite
python tests/run_tests.py
```

### 4. Visual Testing
```powershell
# Open Jupyter notebook
jupyter notebook test_visual_predictions.ipynb
```

## Best Practices

1. **Always activate environment** before running any Python commands
2. **Use `--no-cache-dir`** with pip to save space
3. **Keep requirements.txt updated** when adding new dependencies
4. **Run tests** after making changes
5. **Check logs** in `logs/` directory for debugging
6. **Use `--reload`** during development for auto-restart
7. **Monitor resource usage** with `htop` or Task Manager

## Quick Reference

| Task | Command |
|------|---------|
| Activate env | `conda activate kyc-aml-env` |
| Start API | `python -m uvicorn api.main:app --reload --port 8000` |
| Run tests | `python tests/run_tests.py` |
| Quick test | `python test_quick.py` |
| Download models | `python inference/download_models.py` |
| Check health | `curl http://localhost:8000/health` |
| View docs | `http://localhost:8000/docs` |
| Deactivate | `conda deactivate` |

## Next Steps

After successful setup:

1. ✓ Start the API server
2. ✓ Open http://localhost:8000/docs in browser
3. ✓ Test prediction endpoint with sample images
4. ✓ Run test suite to verify everything works
5. ✓ Try visual testing with Jupyter notebook

## Support

If you encounter issues:
- Check logs in `logs/` directory
- Review error messages carefully
- Ensure all prerequisites are met
- Try manual setup if automated script fails
- Check network connectivity for model downloads
