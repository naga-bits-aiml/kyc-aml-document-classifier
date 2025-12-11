# Docker Deployment Guide

This guide covers building and deploying the KYC/AML Document Classifier using Docker.

## Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed (if using docker-compose)
- At least 2GB free disk space
- Internet connection for downloading models

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t kyc-classifier:latest .

# Run the container
docker run -d \
  --name kyc-aml-classifier \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/training:/app/training \
  --restart unless-stopped \
  kyc-classifier:latest

# View logs
docker logs -f kyc-aml-classifier

# Stop and remove container
docker stop kyc-aml-classifier
docker rm kyc-aml-classifier
```

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

## Support

For issues or questions:
- Check logs: `docker logs kyc-aml-classifier`
- Review configuration: `docker inspect kyc-aml-classifier`
- Test endpoints: Visit http://localhost:8000/docs
