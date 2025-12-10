# Configuration Files

This directory contains configuration files for the KYC/AML Document Classifier application.

## Files

### `model_config.json`
Configuration for model loading and URLs for downloading trained models from GCS.

**Structure:**
- `version`: Current model version (e.g., "v1")
- `model_urls`: Dictionary of model file URLs with signed GCS URLs
- `model_dir`: Local directory where models will be downloaded
- `required_files`: List of files that must be present for the app to run
- `optional_files`: List of files that are nice to have but not required

**Usage:**
```python
import json

with open('conf/model_config.json', 'r') as f:
    config = json.load(f)

version = config['version']
model_urls = config['model_urls']
```

**Updating URLs:**
When signed URLs expire (after ~7 days in current config), regenerate them using:
```bash
# Run the upload_model_to_gcs.ipynb notebook Step 8
# Copy new URLs to this file
```

### `app_config.json`
General application configuration including API settings, model parameters, preprocessing options, and logging.

**Usage:**
```python
import json

with open('conf/app_config.json', 'r') as f:
    config = json.load(f)

port = config['api']['port']
num_classes = config['model']['num_classes']
```

## Environment-Specific Configuration

You can create environment-specific configuration files:
- `model_config.dev.json` - Development environment
- `model_config.prod.json` - Production environment

Load based on environment:
```python
import os
env = os.getenv('ENV', 'dev')
config_file = f'conf/model_config.{env}.json'
```

## Security Notes

⚠️ **Signed URLs contain credentials and expire after the specified duration**
- Current URLs expire on: **Dec 17, 2025** (7 days from generation)
- Do not commit long-lived credentials to version control
- Regenerate URLs periodically using the upload notebook
- Consider using GCS API with service account for production

## Version Management

When deploying a new model version:
1. Update `version` field (e.g., "v1" → "v2")
2. Upload new model to GCS using `upload_model_to_gcs.ipynb`
3. Update `model_urls` with new signed URLs
4. Test the configuration before deployment
