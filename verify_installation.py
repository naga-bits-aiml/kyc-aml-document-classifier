#!/usr/bin/env python
"""
Installation verification script for KYC-AML Document Classifier.
Checks all dependencies and configurations before running the application.
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_python_version():
    """Check if Python version is compatible"""
    print_info("Checking Python version...")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version_str} (compatible)")
        return True
    else:
        print_error(f"Python {version_str} (requires Python 3.8+)")
        return False

def check_package(package_name, import_name=None, version_attr='__version__'):
    """Check if a package is installed and get its version"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, version_attr, 'unknown')
        print_success(f"{package_name}: {version}")
        return True
    except ImportError as e:
        print_error(f"{package_name}: NOT INSTALLED - {str(e)}")
        return False
    except Exception as e:
        print_warning(f"{package_name}: Installed but version unknown - {str(e)}")
        return True

def check_core_dependencies():
    """Check core application dependencies"""
    print_info("Checking core dependencies...")
    
    dependencies = [
        ('FastAPI', 'fastapi'),
        ('Uvicorn', 'uvicorn'),
        ('Python-multipart', 'multipart'),
        ('PyTorch', 'torch'),
        ('TorchVision', 'torchvision'),
        ('Pillow', 'PIL'),
        ('OpenCV', 'cv2'),
        ('NumPy', 'numpy'),
        ('Requests', 'requests'),
    ]
    
    results = []
    for package_name, import_name in dependencies:
        result = check_package(package_name, import_name)
        results.append(result)
    
    return all(results)

def check_test_dependencies():
    """Check test dependencies"""
    print_info("Checking test dependencies (optional)...")
    
    dependencies = [
        ('pytest', 'pytest'),
        ('pytest-html', 'pytest_html'),
        ('pytest-cov', 'pytest_cov'),
        ('httpx', 'httpx'),
    ]
    
    results = []
    for package_name, import_name in dependencies:
        result = check_package(package_name, import_name)
        results.append(result)
    
    if all(results):
        print_success("All test dependencies installed")
    else:
        print_warning("Some test dependencies missing (install with: pip install -r requirements-test.txt)")
    
    return results

def check_file_structure():
    """Check if required files and directories exist"""
    print_info("Checking project structure...")
    
    project_root = Path(__file__).parent
    
    required_files = [
        'api/main.py',
        'inference/inference_engine.py',
        'inference/download_models.py',
        'inference/preprocess.py',
        'conf/app_config.json',
        'conf/model_config.json',
        'conf/logging_config.json',
        'requirements.txt',
    ]
    
    required_dirs = [
        'api',
        'inference',
        'conf',
        'training',
    ]
    
    all_ok = True
    
    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"File: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_ok = False
    
    # Check directories
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.is_dir():
            print_success(f"Directory: {dir_path}")
        else:
            print_error(f"Missing: {dir_path}")
            all_ok = False
    
    return all_ok

def check_model_files():
    """Check if model files are downloaded"""
    print_info("Checking model files...")
    
    project_root = Path(__file__).parent
    training_dir = project_root / 'training'
    
    model_files = {
        'efficientnet_model.pth': 'required',
        'class_indices.json': 'required',
        'training_history.json': 'optional',
    }
    
    all_required_exist = True
    
    for filename, status in model_files.items():
        file_path = training_dir / filename
        
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print_success(f"{filename}: {size_mb:.2f} MB")
        else:
            if status == 'required':
                print_error(f"{filename}: MISSING (required)")
                all_required_exist = False
            else:
                print_warning(f"{filename}: missing (optional)")
    
    if not all_required_exist:
        print_warning("Run 'python inference/download_models.py' to download models")
    
    return all_required_exist

def check_pytorch_device():
    """Check PyTorch device availability"""
    print_info("Checking PyTorch configuration...")
    
    try:
        import torch
        
        # Check CUDA availability
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print_success(f"CUDA available: {device_count} GPU(s) - {device_name}")
        else:
            print_warning("CUDA not available - using CPU (slower inference)")
        
        # Check available device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print_info(f"Default device: {device}")
        
        return True
    except Exception as e:
        print_error(f"PyTorch device check failed: {str(e)}")
        return False

def check_api_config():
    """Check API configuration"""
    print_info("Checking API configuration...")
    
    project_root = Path(__file__).parent
    config_path = project_root / 'conf' / 'app_config.json'
    
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print_success("app_config.json loaded successfully")
        
        # Check key fields
        if 'api' in config:
            api_config = config['api']
            title = api_config.get('title', 'N/A')
            version = api_config.get('version', 'N/A')
            print_info(f"API: {title} v{version}")
        
        return True
    except Exception as e:
        print_error(f"Failed to load app_config.json: {str(e)}")
        return False

def check_port_availability():
    """Check if default port 8000 is available"""
    print_info("Checking port availability...")
    
    import socket
    
    port = 8000
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print_success(f"Port {port} is available")
            return True
    except OSError:
        print_warning(f"Port {port} is already in use (use --port flag to specify different port)")
        return False

def print_summary(results):
    """Print verification summary"""
    print_header("VERIFICATION SUMMARY")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"Total checks: {total_checks}")
    print(f"Passed: {Colors.GREEN}{passed_checks}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total_checks - passed_checks}{Colors.RESET}")
    print()
    
    if all(results.values()):
        print_success("All checks passed! ✓")
        print()
        print_info("You can now start the application:")
        print(f"  {Colors.BOLD}python -m uvicorn api.main:app --reload --port 8000{Colors.RESET}")
        print()
        print_info("API will be available at:")
        print(f"  {Colors.BOLD}http://localhost:8000{Colors.RESET}")
        print(f"  {Colors.BOLD}http://localhost:8000/docs{Colors.RESET} (interactive documentation)")
        return 0
    else:
        print_error("Some checks failed. Please resolve issues above.")
        print()
        print_info("To install missing dependencies:")
        print(f"  {Colors.BOLD}pip install -r requirements.txt{Colors.RESET}")
        print()
        print_info("To download models:")
        print(f"  {Colors.BOLD}python inference/download_models.py{Colors.RESET}")
        return 1

def main():
    """Main verification function"""
    print_header("KYC-AML Document Classifier")
    print_header("Installation Verification")
    
    results = {
        'Python Version': check_python_version(),
        'Core Dependencies': check_core_dependencies(),
        'File Structure': check_file_structure(),
        'Model Files': check_model_files(),
        'PyTorch Device': check_pytorch_device(),
        'API Config': check_api_config(),
        'Port Availability': check_port_availability(),
    }
    
    # Test dependencies check (doesn't affect overall pass/fail)
    print_header("OPTIONAL: Test Dependencies")
    check_test_dependencies()
    
    return print_summary(results)

if __name__ == '__main__':
    sys.exit(main())
