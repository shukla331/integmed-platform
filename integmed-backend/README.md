# IntegMed Backend - API & Database Setup Guide

## 🏗️ Project Structure

```
integmed-backend/
├── alembic/
│   └── versions/
│       ├── 001_initial_schema.py      # Users, patients, encounters, prescriptions
│       ├── 002_fhir_abdm.py           # FHIR resources, ABDM integration
│       └── 003_wearable_data.py       # TimescaleDB wearable data
├── app/
│   ├── api/
│   │   ├── auth.py                     # HPR authentication
│   │   ├── patients.py                 # Patient management
│   │   ├── encounters.py               # Clinical encounters
│   │   ├── prescriptions.py            # Rx with shorthand expansion
│   │   ├── abdm.py                     # ABDM integration
│   │   └── clinical.py                 # Health timeline, analytics
│   ├── core/
│   │   ├── config.py                   # Application settings
│   │   └── database.py                 # DB connection
│   ├── models/
│   │   └── database.py                 # SQLAlchemy models
│   ├── schemas/
│   │   └── api.py                      # Pydantic schemas
│   └── main.py                         # FastAPI application
└── tests/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16
- Redis 7
- TimescaleDB extension

### 1. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic pydantic-settings \
    httpx python-jose python-multipart qrcode pillow redis --break-system-packages
```

### 2. Database Setup

```bash
# Create database
createdb integmed

# Enable TimescaleDB extension
psql integmed -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### 3. Configure Environment

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://integmed:password@localhost:5432/integmed

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256

# ABDM (Sandbox)
ABDM_GATEWAY_URL=https://dev.abdm.gov.in/gateway
ABDM_CLIENT_ID=your_client_id
ABDM_CLIENT_SECRET=your_client_secret

# HPR (Sandbox)
HPR_API_URL=https://hpridsbx.ndhm.gov.in/api

# Environment
ENVIRONMENT=development
DEBUG=True
```

### 4. Run Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Copy migration files to alembic/versions/

# Run migrations
alembic upgrade head
```

### 5. Start Server

```bash
# Development
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🔥 API Examples

### Authentication (HPR-based)

```bash
# Step 1: Initialize authentication (sends OTP)
curl -X POST http://localhost:8000/api/v1/auth/doctor/init \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "+919876543210",
    "purpose": "login"
  }'

# Response: {"txn_id": "abc-123", "message": "OTP sent..."}

# Step 2: Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/doctor/verify \
  -H "Content-Type: application/json" \
  -d '{
    "txn_id": "abc-123",
    "otp": "123456"
  }'

# Response: JWT token + user profile
```

### Create Patient

```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rajesh Kumar",
    "mobile": "+919876543210",
    "gender": "M",
    "year_of_birth": 1985,
    "abha_number": "12-3456-7890-1234",
    "abha_address": "rajesh.kumar@abdm"
  }'
```

### Create Encounter & SOAP Note

```bash
# Create encounter
curl -X POST http://localhost:8000/api/v1/encounters \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid-here",
    "encounter_type": "opd",
    "start_time": "2026-02-09T10:30:00Z",
    "chief_complaint": "Persistent fatigue for 2 weeks"
  }'

# Update with SOAP note
curl -X PATCH http://localhost:8000/api/v1/encounters/{encounter_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "soap_note": {
      "subjective": {
        "chief_complaint": "Persistent fatigue",
        "history_present_illness": "Patient reports 2 weeks of fatigue..."
      },
      "objective": {
        "vitals": {
          "blood_pressure": "140/90",
          "pulse": 78,
          "temperature": 98.6
        },
        "examination": "Patient appears tired..."
      },
      "assessment": {
        "primary_diagnosis": {
          "condition": "Type 2 Diabetes Mellitus",
          "code": "SNOMED-CT:44054006"
        }
      },
      "plan": {
        "medications": ["Metformin", "Amlodipine"],
        "investigations": ["HbA1c", "Lipid profile"],
        "followup": "2 weeks"
      }
    }
  }'
```

### Expand Medication Shorthand

```bash
curl -X POST http://localhost:8000/api/v1/prescriptions/expand-shorthand \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shorthand": "Metf 1000 bd 30d"
  }'

# Response: Fully expanded medication object
{
  "generic_name": "METFORMIN",
  "strength": "1000mg",
  "dosage_form": "tablet",
  "route": "oral",
  "frequency": "Twice daily",
  "duration_days": 30,
  "quantity": 60,
  "instructions": "Take after meals",
  "rxnorm_code": "6809"
}
```

### Check Drug Interactions

```bash
curl -X POST http://localhost:8000/api/v1/prescriptions/check-interactions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "medications": [
      {
        "generic_name": "METFORMIN",
        "strength": "1000mg",
        "frequency": "Twice daily",
        "duration_days": 30
      }
    ],
    "ayush_medications": [
      {
        "name": "Triphala Churna",
        "dose": "5g",
        "frequency": "Twice daily",
        "duration_days": 30
      }
    ],
    "patient_conditions": ["type_2_diabetes", "hypertension"]
  }'

# Response: Interactions, contraindications, safety score
```

### Create & Sign Prescription

```bash
# Create draft
curl -X POST http://localhost:8000/api/v1/prescriptions/draft \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "encounter_id": "encounter-uuid",
    "medications": [
      {
        "generic_name": "METFORMIN",
        "strength": "1000mg",
        "dosage_form": "tablet",
        "route": "oral",
        "frequency": "Twice daily",
        "duration_days": 30,
        "quantity": 60,
        "instructions": "Take after meals"
      }
    ]
  }'

# Sign prescription
curl -X POST http://localhost:8000/api/v1/prescriptions/{prescription_id}/sign \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Response includes QR code (base64) and signature hash
```

### Get Health Timeline

```bash
curl -X GET "http://localhost:8000/api/v1/clinical/health-graph/{patient_id}?include_wearables=true&include_ayush=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Response: Integrated timeline with all health events
```

## 🗄️ Database Schema Overview

### Core Tables

- **users** - Doctors, nurses, admin (HPR-linked)
- **patients** - Patient records (ABHA-linked)
- **clinics** - Hospital/clinic information
- **encounters** - Clinical visits with SOAP notes
- **prescriptions** - Digital prescriptions with signatures

### FHIR & Integration

- **fhir_resources** - JSONB storage for all FHIR resource types
- **abdm_consents** - Consent management
- **abdm_data_requests** - Health data fetch tracking

### Time-Series

- **wearable_data** - TimescaleDB hypertable for IoT data
- **wearable_daily_avg** - Continuous aggregate (auto-updated)

### Compliance

- **audit_logs** - Complete audit trail (7-year retention)

## 🔐 Security Features

1. **HPR Authentication** - Doctor verification via government registry
2. **JWT Tokens** - Secure stateless authentication
3. **RBAC** - Role-based permissions (MBBS vs BAMS restrictions)
4. **Audit Logging** - All actions logged with IP and user agent
5. **Data Encryption** - At rest (PostgreSQL) and in transit (TLS)

## 🌐 ABDM Integration

The API includes full ABDM (Ayushman Bharat Digital Mission) integration:

1. **Discovery** - Find patient records across India
2. **Consent** - Request patient consent for data access
3. **Health Data Fetch** - Retrieve FHIR bundles from HIPs
4. **Push to Locker** - Send prescriptions to patient's digital locker

See `app/api/abdm.py` for implementation details.

## 📊 Performance Optimizations

- **Connection Pooling** - 10 connections, 20 max overflow
- **JSONB Indexes** - GIN indexes for FHIR resource queries
- **TimescaleDB** - Automatic partitioning for time-series data
- **Continuous Aggregates** - Pre-computed daily averages for wearables
- **Composite Indexes** - Optimized for patient timeline queries

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/

# Integration tests (requires running database)
pytest tests/integration/
```

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

See technical architecture document for full Kubernetes manifests.

## 🔧 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Check TimescaleDB extension
psql integmed -c "SELECT * FROM timescaledb_information.hypertables;"
```

### Migration Issues

```bash
# Check migration status
alembic current

# Rollback one version
alembic downgrade -1

# Fresh start (WARNING: destroys data)
alembic downgrade base
alembic upgrade head
```

### API Issues

```bash
# Check logs
tail -f /var/log/integmed/api.log

# Test health endpoint
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/ready
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [ABDM Developer Portal](https://sandbox.abdm.gov.in/)
- [TimescaleDB Docs](https://docs.timescale.com/)
- [FHIR R4 Specification](https://www.hl7.org/fhir/R4/)

## 🤝 Contributing

1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description

## 📄 License

Proprietary - Apollo Hospital Group

---

**Questions?** Contact the engineering team or refer to the Technical Architecture document.
