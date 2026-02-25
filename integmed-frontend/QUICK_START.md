# IntegMed Quick Start - 30-Minute Setup Guide

## 📋 Prerequisites Check
```
✅ Python 3.11.8    - Already installed
✅ Docker 29.2.0    - Already installed
⏳ PostgreSQL       - NEED TO INSTALL
⏳ Node.js          - NEED TO INSTALL
```

---

## ⚡ 30-Minute Installation

### Step 1: Install PostgreSQL (10 minutes)
1. Download: https://www.postgresql.org/download/windows/
2. **Password**: `integmed_dev_password`
3. **Port**: `5432`
4. Finish installation

### Step 2: Install Node.js (5 minutes)
1. Download: https://nodejs.org/ (LTS)
2. Run installer, click OK on all screens
3. Verify: Open PowerShell and run:
   ```powershell
   node --version
   npm --version
   ```

### Step 3: Setup Backend (5 minutes)
```powershell
cd c:\Users\user\Desktop\project medfile\integmed-backend
.\SETUP.bat
```
**Wait for completion**, then:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```
✅ Running on http://localhost:8000

### Step 4: Setup Frontend (5 minutes)
**Open NEW PowerShell window**:
```powershell
cd c:\Users\user\Desktop\project medfile\integmed-frontend
.\SETUP.bat
npm run dev
```
✅ Running on http://localhost:3000

---

## 🌐 Access Points

| URL | Purpose |
|-----|---------|
| http://localhost:3000 | **Main Application** |
| http://localhost:8000 | Backend API |
| http://localhost:8000/api/v1/docs | **API Documentation** |
| localhost:5432 | Database (integmed / integmed_dev_password) |

---

## 🔑 Login Credentials (to add - create test user)
```
Username: admin
Password: admin123
```
*(Create these after first backend startup)*

---

## 🛑 Stopping Services
```powershell
# Press Ctrl+C in each terminal to stop services
Ctrl+C  # Terminal 1 (backend)
Ctrl+C  # Terminal 2 (frontend)
```

---

## ❌ If Something Goes Wrong

### "Python not found"
```powershell
# Reinstall Python from: https://www.python.org/downloads/
# Add to PATH during installation
```

### "npm not found"
```powershell
# Install Node.js from: https://nodejs.org/
```

### "Database connection failed"
```powershell
# Check PostgreSQL is running:
# Windows: Services app → PostgreSQL → Status
# Verify password: integmed_dev_password
```

### "Port 3000 already in use"
```powershell
# Kill process:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## 📚 Full Documentation

For detailed setup, troubleshooting, and configuration:
📄 **LOCAL_SETUP_GUIDE.md** - Complete guide
📄 **IMPLEMENTATION_SUMMARY.md** - Architecture overview

---

## ✅ Success Checklist

- [ ] PostgreSQL installed and running
- [ ] Node.js installed
- [ ] Backend startup: `uvicorn app.main:app --reload`
- [ ] Frontend startup: `npm run dev`
- [ ] Frontend loads at http://localhost:3000
- [ ] API docs load at http://localhost:8000/api/v1/docs

---

## 🎯 That's it! You're ready to develop IntegMed! 🎉
