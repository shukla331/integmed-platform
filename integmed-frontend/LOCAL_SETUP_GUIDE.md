# IntegMed System - Complete Local Deployment Guide

## 📋 Current Status

✅ **Completed Setup Steps**:
- Project structure organized
- Backend code copied to deployment folder
- Frontend code copied to deployment folder
- Environment configuration file created (`.env`)
- Database initialization script created
- Setup scripts generated for both backend and frontend
- Deployment documentation created

⚠️ **Current Issue**:
- Docker daemon unresponsive on this system
- **Solution**: Use manual local deployment (recommended for development)

---

## 🚀 Local Setup (Without Docker) - Recommended for Development

This approach runs all services natively on Windows, making development easier.

### Prerequisites Checklist

- [x] Python 3.11.8 - **Already installed**
- [ ] PostgreSQL 16 (or MySQL)
- [ ] Redis (optional, for caching)
- [ ] Node.js 18+ (for frontend)
- [ ] npm/yarn

### Install PostgreSQL (Windows)

1. Download: https://www.postgresql.org/download/windows/
2. Run installer:
   - Accept default settings
   - **Password**: `integmed_dev_password`
   - **Port**: 5432
   - Install pgAdmin if you want database UI
3. After installation:
   - Open pgAdmin or psql command line
   - Create database:
     ```sql
     CREATE DATABASE integmed OWNER integmed;
     ```

### Install Node.js (Windows)

1. Download: https://nodejs.org/ (LTS version)
2. Run installer - accept default settings
3. Verify installation:
   ```powershell
   node --version
   npm --version
   ```

### Install Redis (Optional but Recommended)

**Option A: Using Windows Subsystem for Linux**
```powershell
wsl -d Ubuntu
sudo apt-get update
sudo apt-get install redis-server
redis-server --port 6379
```

**Option B: Using pre-built Windows binary**
- Download: https://github.com/microsoftarchive/redis/releases
- Extract and run `redis-server.exe`

---

## ⚙️ Database Configuration

Edit `.env` file in `integmed-deployment` folder:

```env
# Local PostgreSQL connection
DATABASE_URL=postgresql://integmed:integmed_dev_password@localhost:5432/integmed
REDIS_URL=redis://localhost:6379/0  # Only if Redis is installed
```

---

## 📦 Backend Setup & Launch

### Step 1: Setup Backend Environment

```powershell
cd c:\Users\user\Desktop\project medfile\integmed-backend

# Run the setup script
.\SETUP.bat

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head  # Run database migrations
```

### Step 2: Start Backend API

```powershell
cd c:\Users\user\Desktop\project medfile\integmed-backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Backend will be available at**:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

---

## 🎨 Frontend Setup & Launch

### Step 1: Setup Frontend Environment

```powershell
cd c:\Users\user\Desktop\project medfile\integmed-frontend

# Run the setup script
.\SETUP.bat

# Or manually:
npm install
```

### Step 2: Start Frontend Dev Server

```powershell
cd c:\Users\user\Desktop\project medfile\integmed-frontend
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

**Expected output**:
```
▲ Next.js 14.0.0
- Local:        http://localhost:3000
```

**Frontend will be available at**:
- http://localhost:3000
- Login page: http://localhost:3000/login
- Dashboard: http://localhost:3000/dashboard

---

## 🔑 API Documentation & Testing

Once backend is running, access:

**Interactive API Documentation (Swagger)**:
- http://localhost:8000/api/v1/docs

**Key Endpoints**:
```
POST   /api/v1/auth/login          - User login
GET    /api/v1/patients            - List patients
POST   /api/v1/patients            - Create patient
GET    /api/v1/prescriptions       - List prescriptions
POST   /api/v1/prescriptions       - Create prescription
GET    /api/v1/health              - Health check
```

---

## 🗄️ Database Management

### Access PostgreSQL

```powershell
# Using psql command line
psql -h localhost -U integmed -d integmed

# Using pgAdmin GUI
# Navigate to: http://localhost:5050 (if installed)
```

### Run Migrations

```powershell
cd integmed-backend
alembic upgrade head       # Apply all migrations
alembic history            # View migration history
alembic current            # Check current migration
```

### Common Database Commands

```sql
-- Connect to database
psql -h localhost -U integmed -d integmed

-- List tables
\dt

-- Check migrations table
SELECT * FROM alembic_version;

-- Drop and recreate database (if needed)
DROP DATABASE integmed;
CREATE DATABASE integmed OWNER integmed;
```

---

## 📁 Project Structure

```
integmed-backend/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── api/                 # API routes
│   │   ├── auth.py          # Authentication
│   │   ├── patients.py      # Patient management
│   │   ├── prescriptions.py # Prescription management
│   │   ├── clinical.py      # Clinical data
│   │   └── encounters.py    # Patient encounters
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── core/                # Configuration
├── alembic/
│   └── versions/            # Database migrations
└── requirements.txt         # Python dependencies

integmed-frontend/
├── app/
│   ├── page.tsx             # Home page
│   ├── login/               # Login page
│   ├── dashboard/           # Main dashboard
│   └── layout.tsx           # Root layout
├── components/              # React components
├── lib/
│   ├── api.ts               # API client
│   └── store.ts             # State management
├── public/                  # Static assets
└── package.json             # NPM dependencies
```

---

## 🔐 Environment Variables Configuration

The `.env` file has been created with default values. To add third-party services:

### ABDM Health Data Exchange (India)
```env
ABDM_GATEWAY_URL=https://dev.abdm.gov.in/gateway
ABDM_CLIENT_ID=your_client_id
ABDM_CLIENT_SECRET=your_client_secret
```

### Twilio (SMS/Voice)
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Whisper AI (Medical Scribe)
```env
WHISPER_API_KEY=sk-your-api-key
```

### Wearable APIs
```env
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_client_secret
APPLE_HEALTH_TEAM_ID=XXXXXXXXXX
```

---

## 🛠️ Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```powershell
# Solution: Activate venv and install dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Error**: `database connection refused`
```powershell
# Solution: Ensure PostgreSQL is running
# Windows: Check Services or pgAdmin
# Verify DATABASE_URL in .env is correct
psql -h localhost -U integmed -d integmed  # Test connection
```

### Frontend won't start

**Error**: `npm: command not found`
- Solution: Install Node.js from https://nodejs.org/

**Error**: `Cannot find module 'next'`
```powershell
npm install
npm run dev
```

### Port already in use

**Frontend (Port 3000)**:
```powershell
# Find process using port 3000
netstat -ano | findstr :3000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

**Backend (Port 8000)**:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 🚀 Next Steps

### 1. Get System Running
- [ ] Install PostgreSQL
- [ ] Install Node.js
- [ ] Run backend setup: `.\SETUP.bat`
- [ ] Run frontend setup: `.\SETUP.bat`

### 2. Start Services
- [ ] Start backend: `uvicorn app.main:app --reload`
- [ ] Start frontend: `npm run dev`
- [ ] Access: http://localhost:3000

### 3. Test System
- [ ] Login with test credentials
- [ ] Create test patient
- [ ] Create test prescription
- [ ] View dashboard

### 4. Configuration
- [ ] Add ABDM credentials to `.env`
- [ ] Add Twilio credentials for SMS
- [ ] Configure email service
- [ ] Setup wearable API connections

### 5. Production Deployment
- Once tested locally, use Docker for consistent deployment
- Configure AWS EKS for cloud deployment
- Set up CI/CD pipeline

---

## 📞 Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Python Alembic**: https://alembic.sqlalchemy.org/

---

## 📄 Files Created

- ✅ `integmed-deployment/.env` - Environment configuration
- ✅ `integmed-deployment/backend/init.sql` - Database initialization
- ✅ `integmed-deployment/DEPLOYMENT_GUIDE.md` - Docker deployment guide
- ✅ `integmed-backend/SETUP.bat` - Backend setup script
- ✅ `integmed-frontend/SETUP.bat` - Frontend setup script
- ✅ **This file** - Complete local deployment guide

---

**Ready to begin?** Start with installing PostgreSQL and Node.js, then run the SETUP.bat scripts!
