# Docker Lifecycle - Quick Summary

A concise overview of the Docker container lifecycle from build to cleanup.

---

## 📦 Docker Lifecycle Stages

```
1. BUILD → 2. CREATE → 3. START → 4. RUN → 5. STOP → 6. REMOVE
```

---

## 1️⃣ BUILD - Create Image

**Command:**
```bash
docker build -t image-name .
# or
docker compose build
```

**What Happens:**
- Reads `Dockerfile`
- Downloads base image (e.g., `python:3.10-slim`)
- Executes each instruction (RUN, COPY, etc.)
- Creates layers
- Tags final image

**Result:** Docker image stored locally

**Check Images:**
```bash
docker images
```

---

## 2️⃣ CREATE - Prepare Container

**Command:**
```bash
docker create --name container-name image-name
# or (automatic with compose)
docker compose create
```

**What Happens:**
- Allocates container from image
- Sets up networking
- Prepares volumes
- Configures environment variables
- Does NOT start the container yet

**Result:** Container exists but not running

**Check Containers:**
```bash
docker ps -a  # Shows all containers including stopped
```

---

## 3️⃣ START - Launch Container

**Command:**
```bash
docker start container-name
# or
docker compose start
```

**What Happens:**
- Starts the container's main process
- Executes CMD or ENTRYPOINT from Dockerfile
- Container becomes "running"

**Result:** Container is running

---

## 4️⃣ RUN - Create + Start (Combined)

**Command:**
```bash
docker run -d --name container-name image-name
# or
docker compose up -d
```

**What Happens:**
- Creates container (if doesn't exist)
- Starts container
- All in one command
- `-d` runs in detached mode (background)

**Result:** Container created and running

**Check Running Containers:**
```bash
docker ps
```

---

## 5️⃣ STOP - Graceful Shutdown

**Command:**
```bash
docker stop container-name
# or
docker compose stop
```

**What Happens:**
- Sends SIGTERM signal to main process
- Waits 10 seconds for graceful shutdown
- If still running, sends SIGKILL
- Container state saved

**Result:** Container stopped but not removed

**Alternative - Force Stop:**
```bash
docker kill container-name  # Immediate SIGKILL
```

---

## 6️⃣ REMOVE - Delete Container

**Command:**
```bash
docker rm container-name
# or
docker compose down  # Stops and removes
```

**What Happens:**
- Deletes container
- Frees up resources
- Container must be stopped first (or use `-f`)

**Result:** Container deleted (image remains)

**Remove Image Too:**
```bash
docker rmi image-name
```

---

## 🔄 Common Workflows

### Full Lifecycle - Manual

```bash
# 1. Build image
docker build -t myapp:latest .

# 2. Run container (create + start)
docker run -d --name myapp-container -p 8000:8000 myapp:latest

# 3. View logs
docker logs -f myapp-container

# 4. Stop container
docker stop myapp-container

# 5. Remove container
docker rm myapp-container

# 6. Remove image
docker rmi myapp:latest
```

### Full Lifecycle - Docker Compose

```bash
# 1. Build and run
docker compose up -d --build

# 2. View logs
docker compose logs -f

# 3. Stop (keeps containers)
docker compose stop

# 4. Start again
docker compose start

# 5. Stop and remove
docker compose down

# 6. Remove everything (including volumes)
docker compose down -v
```

---

## 🔍 Container States

```
┌─────────────────────────────────────────────────────┐
│  CREATED → RUNNING → PAUSED → RUNNING → STOPPED     │
│     ↓         ↓                            ↓         │
│  REMOVED ← REMOVED ← ─ ─ ─ ─ ─ ─ ← ─ ─ REMOVED      │
└─────────────────────────────────────────────────────┘
```

| State | Description | Commands |
|-------|-------------|----------|
| **Created** | Container exists but not running | `docker create` |
| **Running** | Container is executing | `docker start`, `docker run` |
| **Paused** | Container frozen (rarely used) | `docker pause` |
| **Stopped** | Container stopped but exists | `docker stop` |
| **Removed** | Container deleted | `docker rm` |

---

## 🛠️ Useful Commands

### Inspect Lifecycle

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List all images
docker images

# Detailed container info
docker inspect container-name

# Container stats (CPU, memory)
docker stats

# View processes inside container
docker top container-name
```

### Restart Strategies

```bash
# Restart container
docker restart container-name

# Auto-restart on failure
docker run -d --restart unless-stopped myapp

# Docker Compose with restart
# In docker-compose.yml:
services:
  myapp:
    restart: unless-stopped
```

### Execute Commands in Running Container

```bash
# Run command in running container
docker exec container-name ls -la

# Interactive shell
docker exec -it container-name /bin/bash

# Run as specific user
docker exec -u root container-name whoami
```

---

## 🧹 Cleanup Commands

### Remove Stopped Containers

```bash
# Remove single container
docker rm container-name

# Remove multiple
docker rm container1 container2

# Remove all stopped containers
docker container prune
```

### Remove Images

```bash
# Remove specific image
docker rmi image-name

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a
```

### Complete Cleanup

```bash
# Remove everything unused (containers, images, networks, cache)
docker system prune -a

# Include volumes
docker system prune -a --volumes

# Check disk space
docker system df
```

---

## 🚀 Our KYC Classifier Lifecycle

### Using Docker Compose

```bash
# BUILD: Create image from Dockerfile
docker compose build

# RUN: Create and start container
docker compose up -d

# CHECK: Verify running
docker ps
curl http://localhost:8000/health

# LOGS: Monitor
docker compose logs -f

# RESTART: Apply changes
docker compose restart

# UPDATE: Pull code and rebuild
git pull
docker compose up -d --build

# STOP: Graceful shutdown
docker compose down

# CLEAN: Remove everything
docker compose down -v
docker system prune -a
```

---

## 📊 Quick Reference Table

| Task | Manual Docker | Docker Compose |
|------|--------------|----------------|
| **Build image** | `docker build -t name .` | `docker compose build` |
| **Create container** | `docker create name` | `docker compose create` |
| **Start** | `docker start name` | `docker compose start` |
| **Run (create+start)** | `docker run -d name` | `docker compose up -d` |
| **Build + run** | `docker build -t name . && docker run -d name` | `docker compose up -d --build` |
| **Stop** | `docker stop name` | `docker compose stop` |
| **Restart** | `docker restart name` | `docker compose restart` |
| **Remove** | `docker rm name` | `docker compose down` |
| **Logs** | `docker logs -f name` | `docker compose logs -f` |
| **Execute command** | `docker exec -it name bash` | `docker compose exec service bash` |
| **List containers** | `docker ps` | `docker compose ps` |

---

## 💡 Best Practices

1. **Always use `-d` for production** - Run containers in detached mode
2. **Use `--build` when code changes** - Rebuild image with latest code
3. **Check logs regularly** - Monitor for errors with `docker compose logs`
4. **Clean up periodically** - Remove unused containers and images
5. **Use restart policies** - Auto-restart containers on failure
6. **Version your images** - Tag with versions, not just `latest`
7. **Don't store data in containers** - Use volumes for persistence

---

## 🔗 Image vs Container

| Image | Container |
|-------|-----------|
| Template/Blueprint | Running instance |
| Read-only | Can write (lost on removal) |
| One image → Many containers | Each container from one image |
| Created with `build` | Created with `run` or `create` |
| Stored as layers | Has runtime state |
| Like a class | Like an object |

**Analogy:**
- **Image** = Recipe (instructions)
- **Container** = Cooked dish (result)

You can cook (run) many dishes (containers) from one recipe (image)!

---

**That's the Docker lifecycle! 🐳**
