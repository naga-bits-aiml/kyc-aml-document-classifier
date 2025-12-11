#!/bin/bash
#
# KYC Classifier - Supervisor Setup Script
# This script installs Supervisor, sets up Conda environment, and configures the service
#
# Usage:
#   chmod +x setup_supervisor.sh
#   ./setup_supervisor.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME="kyc-aml-document-classifier"
CONDA_ENV_NAME="kyc-aml-env"
PYTHON_VERSION="3.10"
SERVICE_NAME="kyc-classifier"
PORT=8000

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}KYC Classifier - Supervisor Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Project Root: ${GREEN}$PROJECT_ROOT${NC}"
echo -e "Conda Environment: ${GREEN}$CONDA_ENV_NAME${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux. Detected: $OSTYPE"
    exit 1
fi

print_status "Detected Linux system"

# Update system
echo ""
print_info "Step 1: Updating system packages..."
sudo apt-get update -qq
print_status "System packages updated"

# Install Supervisor
echo ""
print_info "Step 2: Installing Supervisor..."
if command -v supervisord &> /dev/null; then
    print_warning "Supervisor already installed: $(supervisord --version)"
else
    sudo apt-get install -y supervisor
    print_status "Supervisor installed: $(supervisord --version)"
fi

# Ensure supervisor is running
sudo systemctl enable supervisor
sudo systemctl start supervisor
print_status "Supervisor service started"

# Install Miniconda if not present
echo ""
print_info "Step 3: Installing Miniconda..."
if command -v conda &> /dev/null; then
    print_warning "Conda already installed: $(conda --version)"
    CONDA_PATH=$(which conda)
    CONDA_BASE=$(dirname $(dirname $CONDA_PATH))
else
    print_info "Downloading Miniconda installer..."
    MINICONDA_INSTALLER="/tmp/miniconda.sh"
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O $MINICONDA_INSTALLER
    
    print_info "Installing Miniconda to ~/miniconda3..."
    bash $MINICONDA_INSTALLER -b -p ~/miniconda3
    rm $MINICONDA_INSTALLER
    
    # Initialize conda
    ~/miniconda3/bin/conda init bash
    source ~/.bashrc
    
    CONDA_BASE="$HOME/miniconda3"
    print_status "Miniconda installed successfully"
fi

# Get conda paths
CONDA_BIN="$CONDA_BASE/bin/conda"
print_status "Conda base: $CONDA_BASE"

# Create or update conda environment
echo ""
print_info "Step 4: Creating Conda environment '$CONDA_ENV_NAME'..."

if $CONDA_BIN env list | grep -q "^$CONDA_ENV_NAME "; then
    print_warning "Environment '$CONDA_ENV_NAME' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing environment..."
        $CONDA_BIN env remove -n $CONDA_ENV_NAME -y
        print_info "Creating fresh environment..."
        $CONDA_BIN create -n $CONDA_ENV_NAME python=$PYTHON_VERSION -y
        print_status "Environment recreated"
    else
        print_warning "Using existing environment"
    fi
else
    $CONDA_BIN create -n $CONDA_ENV_NAME python=$PYTHON_VERSION -y
    print_status "Environment '$CONDA_ENV_NAME' created"
fi

# Get Python executable path
PYTHON_PATH="$CONDA_BASE/envs/$CONDA_ENV_NAME/bin/python"
UVICORN_PATH="$CONDA_BASE/envs/$CONDA_ENV_NAME/bin/uvicorn"

print_status "Python path: $PYTHON_PATH"

# Install dependencies
echo ""
print_info "Step 5: Installing Python dependencies..."
print_info "This may take a few minutes..."

# Activate environment and install packages
source $CONDA_BASE/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME

# Install core dependencies
print_info "Installing core dependencies from requirements.txt..."
pip install -q --no-cache-dir -r "$PROJECT_ROOT/requirements.txt"

# Verify critical packages
print_info "Verifying installations..."
$PYTHON_PATH -c "import fastapi; import uvicorn; import torch; import PIL; import cv2" && \
    print_status "All critical packages installed successfully" || \
    { print_error "Package installation verification failed"; exit 1; }

conda deactivate

# Create Supervisor configuration
echo ""
print_info "Step 6: Creating Supervisor configuration..."

SUPERVISOR_CONF="/etc/supervisor/conf.d/${SERVICE_NAME}.conf"
TEMP_CONF="/tmp/${SERVICE_NAME}.conf"

cat > $TEMP_CONF << EOF
[program:${SERVICE_NAME}]
command=${UVICORN_PATH} api.main:app --host 0.0.0.0 --port ${PORT} --workers 1
directory=${PROJECT_ROOT}
user=${USER}
autostart=true
autorestart=true
startsecs=10
startretries=3
stopwaitsecs=10
redirect_stderr=true
stdout_logfile=${PROJECT_ROOT}/logs/supervisor-%(program_name)s.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=${PROJECT_ROOT}/logs/supervisor-%(program_name)s-error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
environment=PATH="${CONDA_BASE}/envs/${CONDA_ENV_NAME}/bin:%(ENV_PATH)s",PYTHONUNBUFFERED="1"
EOF

# Move to supervisor conf directory
sudo mv $TEMP_CONF $SUPERVISOR_CONF
print_status "Supervisor configuration created: $SUPERVISOR_CONF"

# Create logs directory if not exists
mkdir -p "$PROJECT_ROOT/logs"
print_status "Logs directory ready: $PROJECT_ROOT/logs"

# Reload Supervisor
echo ""
print_info "Step 7: Reloading Supervisor configuration..."
sudo supervisorctl reread
sudo supervisorctl update
print_status "Supervisor configuration reloaded"

# Display configuration summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup Complete! ✓${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Configuration Summary:${NC}"
echo -e "  Project Root:    ${GREEN}$PROJECT_ROOT${NC}"
echo -e "  Conda Env:       ${GREEN}$CONDA_ENV_NAME${NC}"
echo -e "  Python Path:     ${GREEN}$PYTHON_PATH${NC}"
echo -e "  Service Name:    ${GREEN}$SERVICE_NAME${NC}"
echo -e "  Port:            ${GREEN}$PORT${NC}"
echo -e "  Supervisor Conf: ${GREEN}$SUPERVISOR_CONF${NC}"
echo -e "  Logs Directory:  ${GREEN}$PROJECT_ROOT/logs${NC}"
echo ""
echo -e "${YELLOW}Commands to Manage Service:${NC}"
echo ""
echo -e "${GREEN}# Start the service${NC}"
echo -e "  sudo supervisorctl start ${SERVICE_NAME}"
echo ""
echo -e "${GREEN}# Stop the service${NC}"
echo -e "  sudo supervisorctl stop ${SERVICE_NAME}"
echo ""
echo -e "${GREEN}# Restart the service${NC}"
echo -e "  sudo supervisorctl restart ${SERVICE_NAME}"
echo ""
echo -e "${GREEN}# Check service status${NC}"
echo -e "  sudo supervisorctl status ${SERVICE_NAME}"
echo ""
echo -e "${GREEN}# View all services${NC}"
echo -e "  sudo supervisorctl status"
echo ""
echo -e "${GREEN}# View logs (real-time)${NC}"
echo -e "  tail -f ${PROJECT_ROOT}/logs/supervisor-${SERVICE_NAME}.log"
echo ""
echo -e "${GREEN}# View error logs${NC}"
echo -e "  tail -f ${PROJECT_ROOT}/logs/supervisor-${SERVICE_NAME}-error.log"
echo ""
echo -e "${GREEN}# View logs with supervisor${NC}"
echo -e "  sudo supervisorctl tail -f ${SERVICE_NAME}"
echo ""
echo -e "${GREEN}# Test API${NC}"
echo -e "  curl http://localhost:${PORT}/health"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Start the service:  ${GREEN}sudo supervisorctl start ${SERVICE_NAME}${NC}"
echo -e "  2. Check status:       ${GREEN}sudo supervisorctl status ${SERVICE_NAME}${NC}"
echo -e "  3. Test API:           ${GREEN}curl http://localhost:${PORT}/health${NC}"
echo -e "  4. View in browser:    ${GREEN}http://YOUR_VM_IP:${PORT}/docs${NC}"
echo ""
echo -e "${BLUE}Happy Classifying! 📄${NC}"
