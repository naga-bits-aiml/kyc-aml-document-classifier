"""
Model downloader utility for KYC/AML Document Classifier.

This script loads configuration and downloads model files if they don't exist locally.
Can be used in both Docker builds and application startup.
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


# Get the project root directory (parent of inference folder)
# This works regardless of where the script is called from because
# __file__ is always the absolute path to THIS file (download_models.py)
SCRIPT_DIR = Path(__file__).resolve().parent  # .../inference/
PROJECT_ROOT = SCRIPT_DIR.parent               # .../kyc-aml-document-classifier/


def load_config(config_path: str = "conf/model_config.json") -> dict:
    """Load model configuration from JSON file."""
    # Make path relative to project root
    config_full_path = PROJECT_ROOT / config_path
    
    if not config_full_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_full_path}\n"
            f"Project root: {PROJECT_ROOT}\n"
            f"Expected config at: {config_path}"
        )
    
    with open(config_full_path, 'r') as f:
        return json.load(f)


def get_model_path(config: dict) -> str:
    """
    Get the model path from config.
    Uses 'model_path' if available, otherwise falls back to 'model_dir'.
    Always returns absolute path from project root.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Absolute model directory path
    """
    model_dir = config.get('model_path', config.get('model_dir', 'model'))
    # Convert to absolute path from project root
    return str(PROJECT_ROOT / model_dir)


def check_existing_models(model_dir: str, required_files: List[str]) -> Tuple[List[str], List[str]]:
    """
    Check which model files already exist.
    
    Args:
        model_dir: Directory where models are stored
        required_files: List of required model files
    
    Returns:
        Tuple of (existing_files, missing_files)
    """
    existing = []
    missing = []
    
    for file_name in required_files:
        file_path = os.path.join(model_dir, file_name)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            existing.append(file_name)
            print(f"✓ {file_name} exists ({file_size:.2f} MB)")
        else:
            missing.append(file_name)
            print(f"✗ {file_name} missing")
    
    return existing, missing


def download_file(url: str, destination: str, file_name: str) -> bool:
    """
    Download a file from URL to destination.
    
    Args:
        url: Download URL
        destination: Destination file path
        file_name: Name of file (for logging)
    
    Returns:
        True if download successful, False otherwise
    """
    try:
        print(f"Downloading {file_name}...")
        urllib.request.urlretrieve(url, destination)
        
        file_size = os.path.getsize(destination) / (1024 * 1024)  # MB
        print(f"✅ Downloaded {file_name} ({file_size:.2f} MB)")
        return True
    
    except Exception as e:
        print(f"❌ Failed to download {file_name}: {e}")
        return False


def download_models(config_path: str = "conf/model_config.json", force: bool = False) -> bool:
    """
    Main function to check and download model files.
    
    Args:
        config_path: Path to model configuration JSON (relative to project root)
        force: If True, re-download even if files exist
    
    Returns:
        True if all required files are available, False otherwise
    """
    print("="*60)
    print("MODEL DOWNLOAD UTILITY")
    print("="*60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Script location: {SCRIPT_DIR}")
    
    # Load configuration
    try:
        config = load_config(config_path)
        print(f"\n✓ Loaded configuration from {config_path}")
        print(f"  Version: {config['version']}")
    except Exception as e:
        print(f"\n❌ Failed to load configuration: {e}")
        return False
    
    # Get model directory path (supports both model_path and model_dir)
    model_dir = get_model_path(config)
    print(f"  Model directory: {model_dir}")
    
    # Create model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    print(f"\n✓ Model directory ready: {model_dir}")
    
    # Get required files
    required_files = config.get('required_files', [])
    model_urls = config.get('model_urls', {})
    
    print(f"\n📋 Required files: {len(required_files)}")
    for file_name in required_files:
        print(f"  - {file_name}")
    
    # Check existing models
    print(f"\n🔍 Checking existing models...")
    existing, missing = check_existing_models(model_dir, required_files)
    
    if not force and len(missing) == 0:
        print(f"\n✅ All required models present ({len(existing)}/{len(required_files)})")
        print("="*60)
        return True
    
    # Download missing models
    if force:
        print(f"\n⚠️  Force mode enabled - re-downloading all files")
        to_download = required_files
    else:
        print(f"\n📥 Need to download {len(missing)} file(s)")
        to_download = missing
    
    downloaded = []
    failed = []
    
    for file_name in to_download:
        if file_name not in model_urls:
            print(f"⚠️  No URL found for {file_name}")
            failed.append(file_name)
            continue
        
        url = model_urls[file_name]
        destination = os.path.join(model_dir, file_name)
        
        if download_file(url, destination, file_name):
            downloaded.append(file_name)
        else:
            failed.append(file_name)
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Already existed: {len(existing)}")
    print(f"Downloaded: {len(downloaded)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print(f"\n❌ Failed to download: {', '.join(failed)}")
        print("="*60)
        return False
    
    print(f"\n✅ All required models available!")
    print("="*60)
    return True


if __name__ == "__main__":
    import sys
    
    # Check for force flag
    force_download = "--force" in sys.argv
    
    # Run download
    success = download_models(force=force_download)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
