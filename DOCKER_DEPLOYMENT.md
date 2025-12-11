# Docker Deployment Guide - KYC Document Classifier

Complete guide for deploying the KYC-AML Document Classifier using Docker on your GCP VM (or any Linux VM).

---

## Prerequisites

✅ **VM with SSH access** (Ubuntu 22.04 recommended)  
✅ **Docker installed** on the VM  
✅ **Git installed** on the VM  
✅ **Port 8000** available

---

## 🚀 Complete Deployment - Step by Step

### Step 1: Install Docker (if not already installed)

```bash
# Update system
sudo apt-get update

# Install Docker and Git
sudo apt-get install -y docker.io docker-compose git

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

**Expected Output:**
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

---

### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/naga-bits-aiml/kyc-aml-document-classifier.git
cd kyc-aml-document-classifier
```

---

## 📦 Docker Lifecycle - Aligned to Your Service

### STAGE 1: BUILD IMAGE

Create a Docker image from your Dockerfile.

```bash
# Build image using docker-compose
docker compose build

# Or build manually
docker build -t kyc-classifier:latest .
```

**What happens:**
- Reads `Dockerfile`
- Downloads Python 3.10 base image
- Installs dependencies from `requirements.txt`
- Copies application code
- Creates image

**Image created:**
```
Repository: kyc-aml-document-classifier-kyc-classifier
Tag:        latest
Size:       ~1.5 GB
```

---

### STAGE 2: VIEW AVAILABLE IMAGES

List all Docker images on your VM.

```bash
# List all images
docker images

# Filter for KYC images only
docker images | grep kyc
```

**Expected Output:**
```
REPOSITORY                                    TAG       IMAGE ID       CREATED         SIZE
kyc-aml-document-classifier-kyc-classifier   latest    abc123def456   2 minutes ago   1.5GB
```

**Detailed image info:**
```bash
# Inspect image
docker image inspect kyc-aml-document-classifier-kyc-classifier:latest

# View image history (layers)
docker history kyc-aml-document-classifier-kyc-classifier:latest
```

---

### STAGE 3: CREATE CONTAINER

Create a container from your image (without starting it).

```bash
# Using docker-compose (creates but doesn't start)
docker compose create

# Or manually create container
docker create \
  --name kyc-aml-classifier \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/training:/app/training \
  --restart unless-stopped \
  kyc-aml-document-classifier-kyc-classifier:latest
```

**Container created:**
```
Name:          kyc-aml-classifier
Status:        Created (not running yet)
Port mapping:  8000 -> 8000
Volumes:       logs, training
```

**View created container:**
```bash
# List all containers (including stopped)
docker ps -a

# Filter for KYC container
docker ps -a | grep kyc
```

---

### STAGE 4: RUN CONTAINER

Start the container and run your service.

```bash
# Start container (if created with docker compose create)
docker compose start

# Or start manually created container
docker start kyc-aml-classifier

# Or create + start in one command
docker compose up -d
```

**What happens:**
- Starts the container
- Executes CMD from Dockerfile (`uvicorn api.main:app`)
- Downloads ML model from GCS (~50MB, first time only)
- Exposes port 8000
- Runs in background (detached mode)

**Container running:**
```
Name:     kyc-aml-classifier
Status:   Up (running)
Port:     0.0.0.0:8000 -> 8000/tcp
```

---

### STAGE 5: VIEW RUNNING CONTAINERS

Check status of all running containers.

```bash
# List running containers
docker ps

# Filter for KYC container
docker ps | grep kyc

# Detailed container info
docker inspect kyc-aml-classifier

# View container stats (CPU, memory)
docker stats kyc-aml-classifier

# Continuous monitoring
docker stats
```

**Expected Output:**
```
CONTAINER ID   IMAGE                                        STATUS         PORTS                    NAMES
abc123def456   kyc-aml-document-classifier-kyc-classifier   Up 2 minutes   0.0.0.0:8000->8000/tcp   kyc-aml-classifier
```

**View logs:**
```bash
# Follow logs in real-time
docker logs -f kyc-aml-classifier

# View last 100 lines
docker logs --tail=100 kyc-aml-classifier

# View logs since last 30 minutes
docker logs --since 30m kyc-aml-classifier
```

---

### STAGE 6: SSH INTO CONTAINER

Access the running container's shell.

```bash
# Open bash shell inside container
docker exec -it kyc-aml-classifier bash

# Or use sh if bash not available
docker exec -it kyc-aml-classifier sh
```

**Inside the container, you can:**
```bash
# Check Python version
python --version

# List files
ls -la

# Check running processes
ps aux

# Test API locally
curl http://localhost:8000/health

# View installed packages
pip list

# Check model files
ls -lh training/

# Exit container (container keeps running)
exit
```

**Run single commands without entering shell:**
```bash
# Check Python version
docker exec kyc-aml-classifier python --version

# List files
docker exec kyc-aml-classifier ls -la /app

# Check disk space
docker exec kyc-aml-classifier df -h

# View model size
docker exec kyc-aml-classifier ls -lh /app/training/
```

---

## 🔄 Container Lifecycle Management

### Stop Container
```bash
# Stop gracefully
docker stop kyc-aml-classifier

# Or using compose
docker compose stop
```

### Start Stopped Container
```bash
# Start existing container
docker start kyc-aml-classifier

# Or using compose
docker compose start
```

### Restart Container
```bash
# Restart
docker restart kyc-aml-classifier

# Or using compose
docker compose restart
```

### Remove Container
```bash
# Stop and remove
docker stop kyc-aml-classifier
docker rm kyc-aml-classifier

# Or using compose (stops and removes)
docker compose down

# Force remove running container
docker rm -f kyc-aml-classifier
```

### Remove Image
```bash
# Remove image (container must be stopped and removed first)
docker rmi kyc-aml-document-classifier-kyc-classifier:latest

# Force remove
docker rmi -f kyc-aml-document-classifier-kyc-classifier:latest
```

---

## 📋 Complete Command Reference

### Image Commands
```bash
# Build
docker compose build
docker build -t kyc-classifier:latest .

# List
docker images
docker images | grep kyc

# Inspect
docker image inspect IMAGE_NAME

# Remove
docker rmi IMAGE_NAME
docker image prune  # Remove unused images
```

### Container Commands
```bash
# Create
docker compose create
docker create --name NAME IMAGE

# Start
docker start CONTAINER_NAME
docker compose start

# Stop
docker stop CONTAINER_NAME
docker compose stop

# Restart
docker restart CONTAINER_NAME
docker compose restart

# Remove
docker rm CONTAINER_NAME
docker compose down

# List
docker ps              # Running only
docker ps -a           # All containers
docker ps | grep kyc   # Filter
```

### Logs & Monitoring
```bash
# Logs
docker logs -f CONTAINER_NAME
docker compose logs -f

# Stats
docker stats CONTAINER_NAME
docker stats  # All containers

# Inspect
docker inspect CONTAINER_NAME
```

### Execute Commands
```bash
# Interactive shell
docker exec -it CONTAINER_NAME bash

# Single command
docker exec CONTAINER_NAME COMMAND

# As root user
docker exec -u root -it CONTAINER_NAME bash
```

---

## 🧹 Cleanup Commands

```bash
# Stop and remove containers
docker compose down

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove everything (containers, images, volumes, networks)
docker system prune -a --volumes

# Check disk usage
docker system df
```

---

## 🔧 Update and Redeploy

```bash
# Navigate to project
cd ~/kyc-aml-document-classifier

# Pull latest code
git pull origin main

# Rebuild image
docker compose build

# Restart with new image
docker compose down
docker compose up -d

# Or in one command
docker compose up -d --build
```

---

## 🏢 Multi-Service VM Management

If running multiple services:

```bash
# View all containers from all services
docker ps -a

# View all images
docker images

# Check port usage
sudo netstat -tulpn | grep LISTEN
sudo ss -tulpn | grep LISTEN

# Resource usage by service
docker stats

# Manage specific service
cd ~/service-directory
docker compose ps      # Status of this service only
docker compose logs -f # Logs for this service only
docker compose restart # Restart this service only
```

---

## ✅ Verify Deployment

```bash
# Check container is running
docker ps | grep kyc

# Test health endpoint
curl http://localhost:8000/health

# Expected response
# {"status":"healthy","model_loaded":true,"timestamp":"..."}

# Test from outside VM (after firewall configured)
curl http://EXTERNAL_IP:8000/health

# Open in browser
# http://EXTERNAL_IP:8000/docs
```

---

## 🎯 Quick Reference Summary

| Task | Command |
|------|---------|
| **Build image** | `docker compose build` |
| **View images** | `docker images \| grep kyc` |
| **Create container** | `docker compose create` |
| **Run container** | `docker compose up -d` |
| **View containers** | `docker ps \| grep kyc` |
| **SSH into container** | `docker exec -it kyc-aml-classifier bash` |
| **View logs** | `docker logs -f kyc-aml-classifier` |
| **Restart** | `docker restart kyc-aml-classifier` |
| **Stop** | `docker stop kyc-aml-classifier` |
| **Remove** | `docker rm kyc-aml-classifier` |

---

## Configuration

### Environment Variables

The application supports the following environment variables:

- `PORT`: Application port (default: 8000)
- `PYTHONUNBUFFERED`: Enable Python unbuffered mode (default: 1)

Example with custom port:

```bash
docker run -d \
  -e PORT=9000 \
  -p 9000:9000 \
  kyc-classifier:latest
```

### Volume Mounts

**Logs Directory** (Recommended):
```bash
-v $(pwd)/logs:/app/logs
```
Persists application logs outside the container.

**Training/Models Directory** (Optional):
```bash
-v $(pwd)/training:/app/training
```
Persists downloaded models outside the container to avoid re-downloading on container restart.

## Accessing the Application

Once running, the API is available at:

- **API Base**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/info

## Testing the Deployment

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-12-11T10:30:00.000000"
}
```

### 2. Test Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.jpg"
```

### 3. Get Supported Classes
```bash
curl http://localhost:8000/classes
```

## Troubleshooting

### Container won't start
```bash
# Check container logs
docker logs kyc-aml-classifier

# Check if port is already in use
netstat -an | grep 8000  # Linux/Mac
netstat -ano | findstr 8000  # Windows
```

### Model not loading
```bash
# Exec into container and check model files
docker exec -it kyc-aml-classifier bash
ls -la /app/training/

# Manually download models inside container
docker exec -it kyc-aml-classifier python inference/download_models.py
```

### Permission issues
```bash
# Ensure directories are writable
chmod -R 755 logs/
chmod -R 755 training/
```

### Memory issues
```bash
# Run with memory limits
docker run -d \
  --memory="2g" \
  --memory-swap="2g" \
  -p 8000:8000 \
  kyc-classifier:latest
```

## Production Deployment

### Best Practices

1. **Use specific version tags** instead of `latest`:
   ```bash
   docker build -t kyc-classifier:v1.0.0 .
   ```

2. **Set resource limits**:
   ```yaml
   # docker-compose.yml
   services:
     kyc-classifier:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
           reservations:
             cpus: '1'
             memory: 1G
   ```

3. **Enable log rotation**:
   ```yaml
   services:
     kyc-classifier:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

4. **Use secrets for sensitive data**:
   ```yaml
   services:
     kyc-classifier:
       secrets:
         - model_api_key
   secrets:
     model_api_key:
       file: ./secrets/api_key.txt
   ```

### Reverse Proxy (Nginx)

Example nginx configuration:

```nginx
upstream kyc_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://kyc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for large file uploads
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

### Cloud Deployment

#### AWS ECS
```bash
# Tag and push to ECR
docker tag kyc-classifier:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/kyc-classifier:latest
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/kyc-classifier:latest
```

#### Google Cloud Run
```bash
# Tag and push to GCR
docker tag kyc-classifier:latest gcr.io/<project-id>/kyc-classifier:latest
docker push gcr.io/<project-id>/kyc-classifier:latest

# Deploy
gcloud run deploy kyc-classifier \
  --image gcr.io/<project-id>/kyc-classifier:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
# Tag and push to ACR
docker tag kyc-classifier:latest <registry-name>.azurecr.io/kyc-classifier:latest
docker push <registry-name>.azurecr.io/kyc-classifier:latest

# Deploy
az container create \
  --resource-group <resource-group> \
  --name kyc-classifier \
  --image <registry-name>.azurecr.io/kyc-classifier:latest \
  --cpu 2 --memory 4 \
  --ip-address Public \
  --ports 8000
```

## Monitoring

### Container Metrics
```bash
# Real-time stats
docker stats kyc-aml-classifier

# Inspect container
docker inspect kyc-aml-classifier
```

### Application Logs
```bash
# Follow logs
docker logs -f --tail 100 kyc-aml-classifier

# Export logs
docker logs kyc-aml-classifier > app.log 2>&1
```

### Health Check Status
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' kyc-aml-classifier
```

## Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Cleanup
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (careful!)
docker system prune -a --volumes
```

## Security Considerations

1. **Run as non-root user** ✓ (Already configured in Dockerfile)
2. **Scan for vulnerabilities**:
   ```bash
   docker scan kyc-classifier:latest
   ```
3. **Use read-only filesystem** (if applicable):
   ```bash
   docker run --read-only -v /app/logs:/app/logs -v /tmp:/tmp kyc-classifier:latest
   ```
4. **Network isolation**:
   ```yaml
   networks:
     kyc-network:
       internal: true  # No external access
   ```

---

## 🔥 GCP Firewall Configuration (For GCP VMs Only)

If deploying on GCP VM, configure firewall to allow external access:

### From Your Local Machine:

```bash
# Create firewall rule for port 8000
gcloud compute firewall-rules create allow-kyc-api \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --target-tags kyc-api \
  --description "Allow access to KYC Document Classifier API"

# Add tag to your VM
gcloud compute instances add-tags YOUR_VM_NAME \
  --tags kyc-api \
  --zone YOUR_ZONE

# Get external IP
gcloud compute instances describe YOUR_VM_NAME \
  --zone YOUR_ZONE \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Access in browser: http://EXTERNAL_IP:8000/docs
```

### Or Using GCP Console:

1. **VPC Network** → **Firewall** → **Create Firewall Rule**
2. Name: `allow-kyc-api`, Direction: Ingress, Target tags: `kyc-api`
3. Source IP ranges: `0.0.0.0/0`, Protocols: `tcp:8000`
4. **Compute Engine** → **VM Instances** → Edit your VM → Add network tag: `kyc-api`

---

## Support

For issues or questions:
- Check logs: `docker logs kyc-aml-classifier`
- Review configuration: `docker inspect kyc-aml-classifier`
- Test endpoints: Visit http://localhost:8000/docs or http://EXTERNAL_IP:8000/docs
