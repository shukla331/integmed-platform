# IntegMed Local Deployment Setup & Troubleshooting Guide

## ✅ Prerequisites Status

- ✅ Docker: Installed (version 29.2.0)
- ✅ Python: Installed (version 3.11.8)
- ⚠️ Docker Daemon: **Not responding** (needs troubleshooting)

## 🚨 Current Issue: Docker Daemon Unresponsive

### Option 1: Restart Docker Desktop (Recommended)

1. **On Windows 10/11**:
   - Press `Ctrl+Shift+Esc` to open Task Manager
   - Look for "Docker Desktop" process
   - Right-click → Restart
   - Wait 30-60 seconds for Docker to fully restart
   - Open PowerShell and run: `docker ps`

2. **Alternative restart method**:
   ```powershell
   # In PowerShell as Administrator:
   Stop-Service Docker
   Start-Service Docker
   docker ps  # Should show output after ~30 seconds
   ```

### Option 2: Manual Local Deployment (Without Docker)

If Docker continues to have issues, you can run services locally:

#### Step 1: Install PostgreSQL
- Download from: https://www.postgresql.org/download/windows/
- Install with password: `integmed_dev_password`
- Port: 5432
- After installation, open pgAdmin and create database `integmed`

#### Step 2: Install Redis
- Download from: https://github.com/microsoftarchive/redis/releases (Windows version)
- Or use Windows Subsystem for Linux (WSL): `wsl -d Ubuntu apt-get install redis-server`

#### Step 3: Setup Backend API
```powershell
cd c:\Users\user\Desktop\project medfile\integmed-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Step 4: Run Database Migrations
```powershell
cd integmed-backend
alembic upgrade head
```

#### Step 5: Start Backend API
```powershell
cd integmed-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 6: Setup Frontend
```powershell
cd integmed-frontend
npm install
npm run dev
```

This will run:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs

---

## 🔧 Docker Troubleshooting Checklist

### Check Docker Daemon Status
```powershell
# Get Docker system info
docker system info

# Check logs (if Windows Service)
Get-EventLog -LogName Application -Source Docker -Newest 10
```

### Clear Docker Build Cache
```powershell
docker system prune -a
docker-compose down -v
```

### Verify Docker Desktop Settings
1. Open Docker Desktop
2. Go to **Settings → Resources**
3. Verify CPU, Memory, Disk allocation are sufficient:
   - Minimum 4GB RAM
   - At least 20GB disk space

### Reinitialize Docker
```powershell
# Reset Docker to factory defaults (CAUTION: Removes all containers)
docker system prune -a --volumes
```

---

## 📋 Environment Configuration

A `.env` file has been created at:
```
integmed-deployment/.env
```

**Key configurations for local development**:
```
DATABASE_URL=postgresql://integmed:integmed_dev_password@localhost:5432/integmed
REDIS_URL=redis://localhost:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000
```

To add third-party service credentials, edit `.env`:
- **ABDM**: Required for Indian health data exchange
- **Twilio**: For SMS/Voice features
- **Whisper API**: For medical scribe AI
- **Fitbit/Apple**: For wearable data

---

## 🚀 Once Docker is Running

```powershell
cd integmed-deployment
docker-compose up -d --build
```

**Monitor the startup**:
```powershell
docker-compose logs -f                    # All services
docker-compose logs -f backend            # Backend only
docker-compose ps                         # Service status
```

**Access the system**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs
- Database: localhost:5432 (integmed / integmed_dev_password)

---

## 🛑 Stop Services

```powershell
# Stop containers (keeps volumes)
docker-compose down

# Stop containers and remove volumes
docker-compose down -v
```

---

## 📞 Next Steps

1. **Restart Docker Desktop** (most likely to resolve immediately)
2. If Docker persists failing, use **Manual Local Deployment** option
3. Once services are running, configure third-party credentials in `.env`
4. Run database migrations: `alembic upgrade head`
5. Access the system and test core flows

**Support**: Check logs and verify network connectivity if services don't start.
