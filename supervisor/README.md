# Supervisor Deployment Guide

This folder contains scripts and configuration for running the KYC Document Classifier as a system service using Supervisor.

## Quick Start

### 1. Make Script Executable

```bash
chmod +x supervisor/setup_supervisor.sh
```

### 2. Run Setup Script

```bash
cd ~/kyc-aml-document-classifier
./supervisor/setup_supervisor.sh
```

**What the script does:**
- ✅ Updates system packages
- ✅ Installs Supervisor
- ✅ Installs Miniconda (if not present)
- ✅ Creates Python 3.10 conda environment
- ✅ Installs all dependencies from requirements.txt
- ✅ Creates Supervisor configuration file
- ✅ Registers the service

---

## Service Management Commands

### Start Service
```bash
sudo supervisorctl start kyc-classifier
```

### Stop Service
```bash
sudo supervisorctl stop kyc-classifier
```

### Restart Service
```bash
sudo supervisorctl restart kyc-classifier
```

### Check Status
```bash
# Check specific service
sudo supervisorctl status kyc-classifier

# Check all services
sudo supervisorctl status
```

### View Logs
```bash
# Follow logs in real-time
tail -f logs/supervisor-kyc-classifier.log

# View error logs
tail -f logs/supervisor-kyc-classifier-error.log

# Using supervisor command
sudo supervisorctl tail -f kyc-classifier
sudo supervisorctl tail -f kyc-classifier stderr
```

### Reload Configuration (after changes)
```bash
sudo supervisorctl reread
sudo supervisorctl update
```

---

## Service Configuration

The Supervisor configuration is created at:
```
/etc/supervisor/conf.d/kyc-classifier.conf
```

**Default settings:**
- **Port**: 8000
- **Auto-start**: Yes (starts on system boot)
- **Auto-restart**: Yes (restarts on failure)
- **Workers**: 1
- **Logs**: `~/kyc-aml-document-classifier/logs/`

---

## Verify Service is Running

```bash
# Check service status
sudo supervisorctl status kyc-classifier

# Expected output:
# kyc-classifier    RUNNING   pid 12345, uptime 0:01:23

# Test API
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","model_loaded":true,"timestamp":"..."}
```

---

## Update Application

When you update your code:

```bash
cd ~/kyc-aml-document-classifier

# Pull latest code
git pull origin main

# Restart service
sudo supervisorctl restart kyc-classifier

# Check logs
tail -f logs/supervisor-kyc-classifier.log
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
tail -100 logs/supervisor-kyc-classifier-error.log

# Check supervisor status
sudo systemctl status supervisor

# Restart supervisor daemon
sudo systemctl restart supervisor

# Check if port is available
sudo netstat -tulpn | grep 8000
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in configuration
sudo nano /etc/supervisor/conf.d/kyc-classifier.conf
# Change: --port 8000 to --port 8080
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart kyc-classifier
```

### Service Crashes Immediately

```bash
# Check error logs
tail -50 logs/supervisor-kyc-classifier-error.log

# Try running manually to see error
source ~/miniconda3/etc/profile.d/conda.sh
conda activate kyc-aml-env
cd ~/kyc-aml-document-classifier
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## Advanced Configuration

### Edit Supervisor Config

```bash
sudo nano /etc/supervisor/conf.d/kyc-classifier.conf
```

**Common changes:**

```ini
# Change number of workers
command=/path/to/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 2

# Change port
command=/path/to/uvicorn api.main:app --host 0.0.0.0 --port 8080 --workers 1

# Add environment variables
environment=PATH="...",PYTHONUNBUFFERED="1",MODEL_CACHE="/custom/path"

# Change log size
stdout_logfile_maxbytes=100MB
stdout_logfile_backups=5
```

**After changes:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart kyc-classifier
```

---

## Multiple Services on Same VM

If running multiple services, each should have its own configuration:

```bash
# List all services
sudo supervisorctl status

# Example output:
# kyc-classifier      RUNNING   pid 12345, uptime 1:23:45
# other-service       RUNNING   pid 12346, uptime 2:34:56
# another-service     RUNNING   pid 12347, uptime 0:45:23

# Manage specific service
sudo supervisorctl restart kyc-classifier
sudo supervisorctl logs kyc-classifier
```

---

## Uninstall / Remove Service

```bash
# Stop service
sudo supervisorctl stop kyc-classifier

# Remove from supervisor
sudo supervisorctl remove kyc-classifier

# Delete configuration
sudo rm /etc/supervisor/conf.d/kyc-classifier.conf

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Optional: Remove conda environment
conda env remove -n kyc-aml-env
```

---

## Service Lifecycle

```
System Boot → Supervisor Starts → Auto-starts kyc-classifier
                                          ↓
                                    Service Running
                                          ↓
                                    (If crashes)
                                          ↓
                                    Auto-restarts
```

---

## Comparison: Supervisor vs Docker

| Feature | Supervisor | Docker |
|---------|-----------|--------|
| **Setup Time** | Fast | Slow (image build) |
| **Resource Usage** | Low | Medium |
| **Isolation** | Partial | Complete |
| **Updates** | Quick (git pull + restart) | Rebuild image |
| **Dependencies** | System-level | Containerized |
| **Best For** | Quick deployment | Production isolation |

---

## Quick Reference

```bash
# Start
sudo supervisorctl start kyc-classifier

# Stop
sudo supervisorctl stop kyc-classifier

# Restart
sudo supervisorctl restart kyc-classifier

# Status
sudo supervisorctl status kyc-classifier

# Logs
tail -f logs/supervisor-kyc-classifier.log

# Update code and restart
git pull && sudo supervisorctl restart kyc-classifier
```

---

**For more details, see:**
- [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md) - Docker alternative
- [README.md](../README.md) - API documentation
