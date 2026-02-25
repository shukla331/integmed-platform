# Integrated Healthcare Platform - Technical Architecture & API Specifications

**Document Version:** 1.0  
**Date:** February 9, 2026  
**Classification:** Confidential - Internal Use Only

---

## Executive Summary

This document outlines the technical architecture for an integrated healthcare platform that bridges Allopathic and AYUSH medical systems through ABDM (Ayushman Bharat Digital Mission) compliance. The platform provides zero-trust authentication, ambient clinical documentation, AI-powered medical scribing, and cross-system prescription management while maintaining strict regulatory compliance with Indian healthcare laws.

### Key Differentiators
- **Dual-Standard Support**: Seamless integration of FHIR R4/R5 (Allopathy) and NAMASTE Portal (AYUSH)
- **Ambient Intelligence**: Real-time AI scribe with medical NLP for SOAP note generation
- **Interaction Shield**: Automated herb-drug contraindication detection
- **Zero-Trust Security**: HPR/ABHA integration with role-based access control
- **Data Sovereignty**: 100% India-resident infrastructure on MeitY-empanelled cloud providers

---

## 1. Technology Stack Recommendations

### 1.1 Backend Architecture

**Primary Framework: Python/FastAPI**

*Rationale:*
- **AI/ML Integration**: Native Python ecosystem for medical NLP, transformers, and ML pipelines
- **Performance**: FastAPI provides async/await support for handling concurrent ABDM API calls
- **FHIR Support**: Mature libraries (`fhir.resources`, `fhirclient`) for R4/R5 compliance
- **Medical Domain**: Extensive medical libraries (spaCy for clinical NLP, medcat for medical entity extraction)
- **Validation**: Pydantic for strict type checking and FHIR resource validation

**Technology Decisions:**

```python
# Core Stack
Backend Framework: FastAPI 0.110+
API Gateway: Kong Gateway (API management, rate limiting, ABDM proxy)
Task Queue: Celery with Redis (for OCR, AI processing, bulk operations)
Real-time: WebSocket support via FastAPI + Redis Pub/Sub
```

### 1.2 Frontend Architecture

**Primary Framework: React + Next.js 14 (App Router)**

*Rationale:*
- **Server Components**: Optimized initial page loads for clinical workflows
- **Command Palette**: Excellent libraries (cmdk) for medical search interfaces
- **Timeline Visualization**: Rich charting libraries (Recharts, D3.js) for health graphs
- **Real-time**: Native WebSocket support for AI scribe streaming
- **Mobile-Ready**: Responsive design with progressive enhancement

**Secondary: React Native (Mobile Apps)**

*For dedicated mobile applications with offline-first capabilities*

```typescript
// Frontend Stack
Framework: Next.js 14 (App Router)
UI Library: Radix UI + Tailwind CSS
State Management: Zustand (lightweight) + TanStack Query (server state)
Forms: React Hook Form + Zod validation
Command Palette: cmdk
Charts: Recharts, Visx
Real-time: Socket.io-client
```

### 1.3 Database Architecture

**Primary Database: PostgreSQL 16**

*Rationale:*
- **JSONB Support**: Native storage for FHIR resources (flexible schema)
- **ACID Compliance**: Critical for prescription/health record integrity
- **Full-Text Search**: Essential for medical record search
- **Extensions**: TimescaleDB for time-series (wearable data), pg_trgm for fuzzy search

**Caching Layer: Redis 7**

*For session management, real-time data, rate limiting*

**Vector Store: pgvector (PostgreSQL extension)**

*For semantic search of medical records and AI-powered clinical decision support*

```sql
-- Database Schema Strategy
Core Tables: Relational (users, appointments, prescriptions)
Health Records: JSONB (FHIR resources - flexible, versioned)
Wearables: TimescaleDB (HRV, sleep, activity data)
Search: Full-text search + vector embeddings for semantic search
```

### 1.4 AI/ML Stack

```python
# Medical NLP & AI
Medical Entity Extraction: MedCAT, scispaCy
Medical Scribe: Fine-tuned Whisper (speech-to-text) + Medical LLM
Drug Interaction: Custom model + RxNorm API integration
OCR: AWS Textract or Azure Document Intelligence (India regions)
Embeddings: BioGPT, PubMedBERT for clinical search
```

### 1.5 Cloud Infrastructure

**Primary: AWS India (Mumbai/Hyderabad) or Azure India**

*Both are MeitY-empanelled for government compliance*

```yaml
Compute: 
  - ECS Fargate (containerized microservices)
  - Lambda (serverless functions for AI processing)
  
Storage:
  - S3/Azure Blob (encrypted document storage)
  - RDS PostgreSQL (managed database with automated backups)
  
Networking:
  - VPC with private subnets (no public internet access for PHI)
  - AWS PrivateLink / Azure Private Endpoints (secure ABDM integration)
  
AI/ML:
  - SageMaker / Azure ML (model training & inference)
  - Textract / Document Intelligence (OCR)
```

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Web App (Next.js)  │  Mobile App (React Native)  │  PWA        │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Kong)                          │
│  - Rate Limiting  - Authentication  - Request Routing            │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (FastAPI)                   │
├─────────────────────────────────────────────────────────────────┤
│  Auth Service  │  Clinical Service  │  Prescription Service      │
│  ABDM Gateway  │  AI Scribe Service │  Document Service          │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL    │  Redis Cache  │  S3 Storage  │  Vector Store   │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                          │
├─────────────────────────────────────────────────────────────────┤
│  ABDM Gateway  │  HPR Registry  │  NAMASTE Portal  │  RxNorm    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Microservices Architecture

```
1. Auth Service
   - HPR/ABHA authentication
   - JWT token management
   - Role-based access control (RBAC)
   - Audit logging

2. Clinical Service
   - SOAP note creation/editing
   - Health Graph aggregation (FHIR + wearables)
   - Timeline visualization
   - Clinical decision support

3. Prescription Service
   - Rx drafting with shorthand expansion
   - NMC compliance validation (generic-first)
   - Drug interaction checking
   - Electronic signature & QR code generation
   - Digital locker push (ABDM)

4. ABDM Gateway Service
   - Discovery, consent, data fetch APIs
   - FHIR resource transformation
   - Health record aggregation
   - Consent management

5. AI Scribe Service
   - Real-time speech-to-text (Whisper)
   - Medical entity extraction (NER)
   - SOAP note generation
   - Context-aware suggestions

6. Document Service
   - OCR processing (old paper records)
   - FHIR resource conversion
   - Document versioning
   - Secure storage & retrieval

7. Integration Service
   - NAMASTE Portal sync
   - SNOMED-CT / LOINC mapping
   - RxNorm drug database
   - Wearable data ingestion
```

---

## 3. API Specifications

### 3.1 Authentication & Authorization APIs

#### 3.1.1 Doctor Authentication (HPR-based)

**Endpoint:** `POST /api/v1/auth/doctor/init`

```json
{
  "mobile": "+919876543210",
  "purpose": "login"
}
```

**Response:**
```json
{
  "txnId": "a825f76b-0696-40f3-864c-5a3a5b389a83",
  "message": "OTP sent to registered mobile"
}
```

**Endpoint:** `POST /api/v1/auth/doctor/verify`

```json
{
  "txnId": "a825f76b-0696-40f3-864c-5a3a5b389a83",
  "otp": "123456"
}
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJSUzI1NiIs...",
  "expiresIn": 3600,
  "doctor": {
    "hprId": "12-3456-7890-1234",
    "name": "Dr. Rajesh Kumar",
    "qualification": "MBBS, MD",
    "registrationNumber": "MH123456",
    "council": "Maharashtra Medical Council",
    "specialization": "Internal Medicine",
    "system": "allopathy",
    "permissions": ["prescribe_schedule_h", "view_patient_records"]
  }
}
```

**Authorization Flow:**
```
1. User enters mobile number
2. System calls ABDM HPR API for OTP
3. User enters OTP
4. System verifies with HPR
5. System fetches doctor profile from HPR
6. System creates local session + JWT
7. Permissions mapped based on qualification (MBBS vs BAMS)
```

**RBAC Matrix:**

| Role | System | Permissions |
|------|--------|-------------|
| MBBS/MD | Allopathy | Full allopathic Rx, Schedule H/X drugs, FHIR records |
| BAMS | Ayurveda | AYUSH Rx only, NAMASTE codes, herbal formulations |
| BHMS | Homeopathy | Homeopathic remedies, potency prescriptions |
| BUMS | Unani | Unani formulations, temperament-based Rx |
| Nurse | Support | Read-only patient records, vital signs entry |

#### 3.1.2 Patient Authentication (ABHA-based)

**Endpoint:** `POST /api/v1/auth/patient/init`

```json
{
  "abhaAddress": "rajesh.kumar@abdm",
  "purpose": "link_records"
}
```

**Response:**
```json
{
  "txnId": "b925f76b-0696-40f3-864c-5a3a5b389a84",
  "authMethods": ["AADHAAR_OTP", "MOBILE_OTP", "DEMOGRAPHICS"],
  "message": "Select authentication method"
}
```

**Endpoint:** `POST /api/v1/auth/patient/verify-aadhaar`

```json
{
  "txnId": "b925f76b-0696-40f3-864c-5a3a5b389a84",
  "otp": "654321"
}
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJSUzI1NiIs...",
  "patient": {
    "abhaNumber": "12-3456-7890-1234",
    "abhaAddress": "rajesh.kumar@abdm",
    "name": "Rajesh Kumar",
    "gender": "M",
    "yearOfBirth": "1985",
    "linkedRecords": 12
  }
}
```

### 3.2 ABDM Integration APIs

#### 3.2.1 Patient Discovery

**Endpoint:** `POST /api/v1/abdm/care-contexts/discover`

**Request:**
```json
{
  "patientId": "rajesh.kumar@abdm",
  "requestId": "499a5a4a-7dda-4f20-9b67-e24589627061",
  "timestamp": "2026-02-09T10:30:00.000Z",
  "query": {
    "patient": {
      "id": "rajesh.kumar@abdm",
      "verifiedIdentifiers": [
        {
          "type": "MOBILE",
          "value": "+919876543210"
        }
      ],
      "name": "Rajesh Kumar",
      "gender": "M",
      "yearOfBirth": 1985
    }
  }
}
```

**Response (from ABDM Gateway):**
```json
{
  "transactionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "patient": {
    "referenceNumber": "rajesh.kumar@abdm",
    "display": "Rajesh Kumar",
    "careContexts": [
      {
        "referenceNumber": "VISIT-001",
        "display": "OPD Visit - Apollo Hospital - 2025-12-15"
      },
      {
        "referenceNumber": "AYUSH-001",
        "display": "Panchakarma Treatment - Kottakkal Arya Vaidya Sala - 2025-11-10"
      }
    ]
  },
  "matchedBy": ["MOBILE", "NAME", "GENDER", "YEAR_OF_BIRTH"]
}
```

#### 3.2.2 Consent Request

**Endpoint:** `POST /api/v1/abdm/consent-requests/init`

**Request:**
```json
{
  "requestId": "5f7a925b-a3bd-4b1d-88e3-1c74f0f91763",
  "timestamp": "2026-02-09T10:35:00.000Z",
  "consent": {
    "purpose": {
      "text": "Clinical Consultation",
      "code": "CAREMGT",
      "refUri": "http://terminology.hl7.org/ValueSet/v3-PurposeOfUse"
    },
    "patient": {
      "id": "rajesh.kumar@abdm"
    },
    "hiu": {
      "id": "INTEGMED-HIU-001"
    },
    "requester": {
      "name": "Dr. Priya Sharma",
      "identifier": {
        "type": "HPR_ID",
        "value": "12-3456-7890-5678"
      }
    },
    "hiTypes": ["OPConsultation", "Prescription", "DiagnosticReport"],
    "permission": {
      "accessMode": "VIEW",
      "dateRange": {
        "from": "2024-01-01T00:00:00.000Z",
        "to": "2026-02-09T23:59:59.000Z"
      },
      "dataEraseAt": "2026-03-09T23:59:59.000Z",
      "frequency": {
        "unit": "HOUR",
        "value": 1,
        "repeats": 1
      }
    }
  }
}
```

**Response:**
```json
{
  "requestId": "5f7a925b-a3bd-4b1d-88e3-1c74f0f91763",
  "consentRequestId": "consent-req-001",
  "timestamp": "2026-02-09T10:35:01.000Z"
}
```

**Notification (Push to patient):**
```json
{
  "notification": {
    "consentRequestId": "consent-req-001",
    "status": "REQUESTED",
    "patient": {
      "id": "rajesh.kumar@abdm"
    },
    "hip": [
      {
        "id": "APOLLO-HIP-001",
        "name": "Apollo Hospital Mumbai"
      },
      {
        "id": "KOTTAKKAL-HIP-001",
        "name": "Kottakkal Arya Vaidya Sala"
      }
    ]
  }
}
```

#### 3.2.3 Health Information Fetch

**Endpoint:** `POST /api/v1/abdm/health-information/request`

**Request:**
```json
{
  "requestId": "3a6a825b-a3bd-4b1d-88e3-1c74f0f91764",
  "timestamp": "2026-02-09T10:40:00.000Z",
  "hiRequest": {
    "consent": {
      "id": "consent-001"
    },
    "dateRange": {
      "from": "2024-01-01T00:00:00.000Z",
      "to": "2026-02-09T23:59:59.000Z"
    },
    "dataPushUrl": "https://integmed.health/api/v1/abdm/data-transfer",
    "keyMaterial": {
      "cryptoAlg": "ECDH",
      "curve": "Curve25519",
      "dhPublicKey": {
        "expiry": "2026-02-09T11:40:00.000Z",
        "parameters": "Curve25519/32byte",
        "keyValue": "MFkwEwYHKoZIzj0CAQYIKoZI..."
      },
      "nonce": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
  }
}
```

**Response:**
```json
{
  "requestId": "3a6a825b-a3bd-4b1d-88e3-1c74f0f91764",
  "transactionId": "txn-001",
  "timestamp": "2026-02-09T10:40:01.000Z"
}
```

**Data Transfer (Push from HIP to our dataPushUrl):**
```json
{
  "transactionId": "txn-001",
  "entries": [
    {
      "content": "encrypted-fhir-bundle-base64",
      "media": "application/fhir+json",
      "checksum": "sha256-hash",
      "careContextReference": "VISIT-001"
    }
  ],
  "keyMaterial": {
    "cryptoAlg": "ECDH",
    "curve": "Curve25519",
    "dhPublicKey": {
      "expiry": "2026-02-09T11:40:00.000Z",
      "parameters": "Curve25519/32byte",
      "keyValue": "MFkwEwYHKoZIzj0CAQYIKoZI..."
    },
    "nonce": "sender-nonce"
  }
}
```

**Decrypted FHIR Bundle Example:**
```json
{
  "resourceType": "Bundle",
  "type": "document",
  "timestamp": "2025-12-15T10:30:00Z",
  "entry": [
    {
      "resource": {
        "resourceType": "Composition",
        "type": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "11488-4",
              "display": "Consultation note"
            }
          ]
        },
        "subject": {
          "reference": "Patient/rajesh-kumar"
        },
        "author": [
          {
            "reference": "Practitioner/dr-sharma"
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "4548-4",
              "display": "Hemoglobin A1c"
            }
          ]
        },
        "valueQuantity": {
          "value": 7.8,
          "unit": "%",
          "system": "http://unitsofmeasure.org",
          "code": "%"
        },
        "interpretation": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "H",
                "display": "High"
              }
            ]
          }
        ]
      }
    }
  ]
}
```

### 3.3 Clinical Workflow APIs

#### 3.3.1 Health Graph / Timeline

**Endpoint:** `GET /api/v1/clinical/health-graph/{patientId}`

**Query Parameters:**
```
?startDate=2024-01-01
&endDate=2026-02-09
&includeWearables=true
&includeAyush=true
```

**Response:**
```json
{
  "patientId": "rajesh.kumar@abdm",
  "timeline": [
    {
      "date": "2026-01-15",
      "type": "wearable",
      "category": "vitals",
      "data": {
        "heartRateVariability": {
          "value": 42,
          "unit": "ms",
          "interpretation": "low_stress",
          "source": "fitbit"
        },
        "sleepQuality": {
          "totalMinutes": 420,
          "deepSleepMinutes": 90,
          "remMinutes": 110,
          "score": 78
        }
      }
    },
    {
      "date": "2025-12-15",
      "type": "allopathic",
      "category": "lab_result",
      "facility": "Apollo Hospital Mumbai",
      "data": {
        "resourceType": "Observation",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "4548-4",
              "display": "Hemoglobin A1c"
            }
          ]
        },
        "valueQuantity": {
          "value": 7.8,
          "unit": "%"
        },
        "interpretation": "high",
        "referenceRange": {
          "low": 4.0,
          "high": 5.6,
          "unit": "%"
        }
      }
    },
    {
      "date": "2025-11-10",
      "type": "ayush",
      "category": "assessment",
      "facility": "Kottakkal Arya Vaidya Sala",
      "data": {
        "prakriti": {
          "primary": "vata",
          "secondary": "pitta",
          "assessment": "vata_pitta_constitution",
          "source": "NAMASTE:PRAKRITI-001"
        },
        "nadiPulse": {
          "rate": 76,
          "quality": "heavy",
          "characteristics": ["slippery", "rapid"],
          "interpretation": "pitta_aggravation"
        },
        "treatment": {
          "type": "panchakarma",
          "procedure": "virechana",
          "duration": 7,
          "outcome": "satisfactory"
        }
      }
    }
  ],
  "summary": {
    "totalEvents": 45,
    "lastVisit": "2026-01-15",
    "chronicConditions": ["type_2_diabetes", "hypertension"],
    "currentMedications": 3,
    "allergyAlerts": ["penicillin"]
  }
}
```

#### 3.3.2 AI Scribe - Real-time SOAP Note

**WebSocket Endpoint:** `wss://integmed.health/ws/scribe/{sessionId}`

**Client → Server (Audio Streaming):**
```json
{
  "type": "audio_chunk",
  "data": "base64-encoded-audio",
  "sampleRate": 16000,
  "format": "pcm",
  "timestamp": 1707471600000
}
```

**Server → Client (Real-time Transcription):**
```json
{
  "type": "transcription",
  "text": "Patient complains of persistent fatigue for the past two weeks",
  "isFinal": false,
  "timestamp": 1707471601000
}
```

**Server → Client (Structured SOAP Update):**
```json
{
  "type": "soap_update",
  "section": "subjective",
  "content": {
    "chiefComplaint": "Persistent fatigue",
    "duration": "2 weeks",
    "severity": "moderate",
    "associatedSymptoms": []
  },
  "confidence": 0.92
}
```

**Server → Client (Clinical Entity Extraction):**
```json
{
  "type": "clinical_entities",
  "entities": [
    {
      "type": "symptom",
      "text": "fatigue",
      "code": {
        "system": "SNOMED-CT",
        "code": "84229001",
        "display": "Fatigue"
      }
    },
    {
      "type": "observation",
      "text": "HbA1c 7.8%",
      "code": {
        "system": "LOINC",
        "code": "4548-4",
        "display": "Hemoglobin A1c"
      },
      "value": 7.8,
      "unit": "%"
    }
  ]
}
```

**REST Endpoint (Save SOAP Note):** `POST /api/v1/clinical/soap-notes`

```json
{
  "patientId": "rajesh.kumar@abdm",
  "encounterId": "encounter-001",
  "sessionId": "scribe-session-123",
  "soap": {
    "subjective": "Patient complains of persistent fatigue for the past two weeks. No fever, cough, or weight loss. Reports increased thirst and frequent urination.",
    "objective": {
      "vitals": {
        "bloodPressure": "140/90",
        "pulse": 78,
        "temperature": 98.6,
        "weight": 75,
        "bmi": 26.2
      },
      "examination": "Patient appears tired. No pallor or icterus. Cardiovascular and respiratory examination unremarkable.",
      "labs": [
        {
          "test": "HbA1c",
          "value": 7.8,
          "unit": "%",
          "code": "LOINC:4548-4",
          "interpretation": "high"
        }
      ]
    },
    "assessment": {
      "primary": {
        "condition": "Type 2 Diabetes Mellitus - poorly controlled",
        "code": "SNOMED-CT:44054006"
      },
      "secondary": [
        {
          "condition": "Hypertension Stage 1",
          "code": "SNOMED-CT:38341003"
        }
      ]
    },
    "plan": {
      "medications": [],
      "investigations": ["Fasting blood sugar", "Lipid profile"],
      "lifestyle": "Advised dietary modifications and regular exercise",
      "followUp": "2 weeks"
    }
  },
  "ayushAssessment": {
    "prakriti": "vata_pitta",
    "vikriti": "kapha_aggravation",
    "nadiPulse": {
      "quality": "heavy",
      "interpretation": "pitta_aggravation"
    }
  },
  "metadata": {
    "doctorId": "dr-priya-sharma",
    "clinicId": "clinic-001",
    "timestamp": "2026-02-09T10:45:00Z",
    "duration": 15
  }
}
```

### 3.4 Prescription APIs

#### 3.4.1 Prescription Drafting (with AI expansion)

**Endpoint:** `POST /api/v1/prescriptions/draft`

**Request (with shorthand):**
```json
{
  "patientId": "rajesh.kumar@abdm",
  "encounterId": "encounter-001",
  "medications": [
    {
      "shorthand": "Metf 500 bd 30d",
      "route": "oral"
    },
    {
      "shorthand": "Amlo 5 od hs 30d",
      "route": "oral"
    }
  ],
  "ayushMedications": [
    {
      "shorthand": "Triphala churna 5g bd 30d",
      "anupana": "warm water"
    }
  ]
}
```

**Response (AI-expanded):**
```json
{
  "prescriptionId": "rx-001",
  "status": "draft",
  "medications": [
    {
      "generic": "METFORMIN",
      "brandSuggestions": ["Glycomet", "Obimet"],
      "strength": "500mg",
      "dosageForm": "tablet",
      "route": "oral",
      "frequency": {
        "code": "BD",
        "display": "Twice daily",
        "times": ["morning", "evening"]
      },
      "duration": {
        "value": 30,
        "unit": "days"
      },
      "quantity": 60,
      "instructions": "Take after meals",
      "snomed": "SNOMED-CT:109081006",
      "rxnorm": "RxNorm:6809"
    },
    {
      "generic": "AMLODIPINE",
      "brandSuggestions": ["Amlodac", "Amlong"],
      "strength": "5mg",
      "dosageForm": "tablet",
      "route": "oral",
      "frequency": {
        "code": "OD",
        "display": "Once daily",
        "times": ["bedtime"]
      },
      "duration": {
        "value": 30,
        "unit": "days"
      },
      "quantity": 30,
      "instructions": "Take at bedtime",
      "snomed": "SNOMED-CT:386864001",
      "rxnorm": "RxNorm:17767"
    }
  ],
  "ayushMedications": [
    {
      "name": "Triphala Churna",
      "type": "churna",
      "dose": "5g",
      "frequency": {
        "code": "BD",
        "display": "Twice daily"
      },
      "anupana": "warm water",
      "duration": {
        "value": 30,
        "unit": "days"
      },
      "namaste": "NAMASTE:HERB-TRIPHALA-001",
      "ingredients": ["Amalaki", "Bibhitaki", "Haritaki"]
    }
  ],
  "validations": {
    "nmc_compliant": true,
    "generic_first": true,
    "interactions": [],
    "contraindications": []
  }
}
```

#### 3.4.2 Interaction Checking

**Endpoint:** `POST /api/v1/prescriptions/check-interactions`

**Request:**
```json
{
  "medications": [
    {
      "generic": "METFORMIN",
      "strength": "500mg"
    },
    {
      "generic": "AMLODIPINE",
      "strength": "5mg"
    }
  ],
  "ayushMedications": [
    {
      "name": "Ashwagandha",
      "dose": "300mg"
    }
  ],
  "patientConditions": ["type_2_diabetes", "hypertension"],
  "patientAllergies": []
}
```

**Response:**
```json
{
  "interactions": [
    {
      "type": "herb_drug",
      "severity": "moderate",
      "drug1": "Ashwagandha",
      "drug2": "Metformin",
      "description": "Ashwagandha may enhance hypoglycemic effects of Metformin",
      "recommendation": "Monitor blood glucose levels closely. Consider adjusting doses.",
      "references": [
        "J Ethnopharmacol. 2015;179:190-197"
      ]
    }
  ],
  "contraindications": [],
  "allergyAlerts": [],
  "safetyScore": 8.2
}
```

#### 3.4.3 Electronic Signature & QR Generation

**Endpoint:** `POST /api/v1/prescriptions/{prescriptionId}/sign`

**Request:**
```json
{
  "signatureMethod": "digital_signature",
  "password": "doctor_pin_or_certificate_password"
}
```

**Response:**
```json
{
  "prescriptionId": "rx-001",
  "status": "signed",
  "signature": {
    "algorithm": "RSA-SHA256",
    "timestamp": "2026-02-09T11:00:00Z",
    "certificate": "base64-encoded-certificate",
    "hash": "sha256-hash-of-prescription"
  },
  "qrCode": {
    "data": "https://integmed.health/rx/rx-001?v=abc123",
    "image": "base64-encoded-qr-image"
  },
  "downloadUrl": "https://integmed.health/api/v1/prescriptions/rx-001/download",
  "abdmPushStatus": "pending"
}
```

**QR Code Content (Verifiable Prescription):**
```json
{
  "type": "prescription",
  "id": "rx-001",
  "patient": {
    "abhaAddress": "rajesh.kumar@abdm",
    "name": "Rajesh Kumar"
  },
  "doctor": {
    "hprId": "12-3456-7890-5678",
    "name": "Dr. Priya Sharma",
    "qualification": "MBBS, MD",
    "registrationNumber": "MH789012"
  },
  "date": "2026-02-09",
  "medications": [
    {
      "generic": "METFORMIN 500mg",
      "frequency": "BD",
      "duration": "30 days"
    }
  ],
  "signature": "sha256-hash",
  "verifyUrl": "https://integmed.health/verify/rx-001"
}
```

### 3.5 Document Processing APIs

#### 3.5.1 Bulk OCR Upload

**Endpoint:** `POST /api/v1/documents/bulk-upload`

**Request (Multipart Form Data):**
```
files: [file1.pdf, file2.jpg, file3.png, ...]
patientId: "rajesh.kumar@abdm"
category: "old_records"
autoProcess: true
```

**Response:**
```json
{
  "batchId": "batch-001",
  "totalFiles": 15,
  "status": "processing",
  "estimatedTime": 120,
  "trackingUrl": "wss://integmed.health/ws/batch/batch-001"
}
```

**WebSocket Progress Updates:**
```json
{
  "batchId": "batch-001",
  "status": "processing",
  "progress": {
    "completed": 3,
    "total": 15,
    "currentFile": "old_report_4.pdf"
  },
  "files": [
    {
      "filename": "old_report_1.pdf",
      "status": "completed",
      "extracted": {
        "text": "Patient: Rajesh Kumar...",
        "entities": [
          {
            "type": "medication",
            "text": "Metformin 500mg BD",
            "confidence": 0.95
          }
        ],
        "fhirResources": [
          {
            "resourceType": "MedicationStatement",
            "medicationCodeableConcept": {
              "coding": [
                {
                  "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                  "code": "6809",
                  "display": "Metformin"
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

---

## 4. Database Schema

### 4.1 Core Tables (PostgreSQL)

```sql
-- Users Table (Doctors, Staff, Admin)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hpr_id VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    mobile VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255),
    system VARCHAR(20) NOT NULL, -- 'allopathy', 'ayurveda', 'homeopathy', 'unani'
    qualification VARCHAR(255),
    registration_number VARCHAR(100) UNIQUE,
    registration_council VARCHAR(255),
    specialization VARCHAR(255),
    role VARCHAR(50) NOT NULL, -- 'doctor', 'nurse', 'admin'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_hpr_id ON users(hpr_id);
CREATE INDEX idx_users_mobile ON users(mobile);

-- Patients Table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    abha_number VARCHAR(17) UNIQUE,
    abha_address VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    mobile VARCHAR(15),
    email VARCHAR(255),
    gender VARCHAR(10),
    date_of_birth DATE,
    year_of_birth INTEGER,
    address JSONB,
    emergency_contact JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patients_abha_number ON patients(abha_number);
CREATE INDEX idx_patients_abha_address ON patients(abha_address);
CREATE INDEX idx_patients_mobile ON patients(mobile);

-- Encounters (Clinical Visits)
CREATE TABLE encounters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES users(id),
    clinic_id UUID REFERENCES clinics(id),
    encounter_type VARCHAR(50) NOT NULL, -- 'opd', 'emergency', 'followup'
    status VARCHAR(50) NOT NULL, -- 'scheduled', 'in_progress', 'completed'
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    chief_complaint TEXT,
    soap_note JSONB, -- Stores full SOAP structure
    ayush_assessment JSONB, -- Prakriti, Vikriti, Nadi, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_encounters_patient_id ON encounters(patient_id);
CREATE INDEX idx_encounters_doctor_id ON encounters(doctor_id);
CREATE INDEX idx_encounters_start_time ON encounters(start_time);

-- Prescriptions
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_number VARCHAR(50) UNIQUE NOT NULL,
    encounter_id UUID NOT NULL REFERENCES encounters(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL, -- 'draft', 'signed', 'dispensed', 'cancelled'
    medications JSONB NOT NULL, -- Array of medication objects
    ayush_medications JSONB, -- Array of Ayurvedic/AYUSH medications
    instructions TEXT,
    
    -- Digital Signature
    signature_hash VARCHAR(255),
    signature_timestamp TIMESTAMPTZ,
    signature_certificate TEXT,
    
    -- QR Code
    qr_code_data TEXT,
    qr_code_image TEXT, -- Base64 encoded
    
    -- ABDM Integration
    abdm_pushed BOOLEAN DEFAULT false,
    abdm_push_timestamp TIMESTAMPTZ,
    
    -- Compliance
    nmc_compliant BOOLEAN DEFAULT true,
    generic_first BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prescriptions_prescription_number ON prescriptions(prescription_number);
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_doctor_id ON prescriptions(doctor_id);
CREATE INDEX idx_prescriptions_status ON prescriptions(status);
```

### 4.2 FHIR Resources Storage (JSONB)

```sql
-- FHIR Resources (Flexible schema for all FHIR types)
CREATE TABLE fhir_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type VARCHAR(50) NOT NULL, -- 'Observation', 'Condition', 'Procedure', etc.
    resource_id VARCHAR(255) NOT NULL, -- FHIR resource ID
    patient_id UUID REFERENCES patients(id),
    encounter_id UUID REFERENCES encounters(id),
    
    -- Full FHIR resource as JSONB
    resource JSONB NOT NULL,
    
    -- Extracted fields for querying
    category VARCHAR(100), -- 'vital-signs', 'laboratory', 'imaging'
    code VARCHAR(100), -- LOINC/SNOMED code
    effective_date DATE,
    value_numeric NUMERIC,
    value_text TEXT,
    
    -- Source tracking
    source VARCHAR(100), -- 'abdm', 'manual', 'wearable', 'lab_integration'
    source_system VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fhir_resource_type ON fhir_resources(resource_type);
CREATE INDEX idx_fhir_patient_id ON fhir_resources(patient_id);
CREATE INDEX idx_fhir_category ON fhir_resources(category);
CREATE INDEX idx_fhir_code ON fhir_resources(code);
CREATE INDEX idx_fhir_effective_date ON fhir_resources(effective_date);

-- GIN index for JSONB queries
CREATE INDEX idx_fhir_resource_gin ON fhir_resources USING gin(resource);
```

### 4.3 Wearable Data (TimescaleDB)

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Wearable Data (Time-series)
CREATE TABLE wearable_data (
    time TIMESTAMPTZ NOT NULL,
    patient_id UUID NOT NULL REFERENCES patients(id),
    device_type VARCHAR(50) NOT NULL, -- 'fitbit', 'apple_watch', 'garmin'
    metric_type VARCHAR(50) NOT NULL, -- 'heart_rate', 'hrv', 'sleep', 'steps'
    value NUMERIC,
    unit VARCHAR(20),
    metadata JSONB, -- Additional device-specific data
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('wearable_data', 'time');

-- Indexes
CREATE INDEX idx_wearable_patient_time ON wearable_data(patient_id, time DESC);
CREATE INDEX idx_wearable_metric_type ON wearable_data(metric_type);
```

### 4.4 ABDM Integration Tables

```sql
-- ABDM Consent Requests
CREATE TABLE abdm_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consent_request_id VARCHAR(255) UNIQUE NOT NULL,
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES users(id),
    purpose VARCHAR(100) NOT NULL,
    hi_types JSONB NOT NULL, -- Array of health info types
    date_range JSONB NOT NULL, -- from, to dates
    status VARCHAR(50) NOT NULL, -- 'requested', 'granted', 'denied', 'expired'
    consent_artifact JSONB, -- Full consent artifact from ABDM
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_abdm_consents_patient_id ON abdm_consents(patient_id);
CREATE INDEX idx_abdm_consents_status ON abdm_consents(status);

-- ABDM Data Requests
CREATE TABLE abdm_data_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    consent_id UUID NOT NULL REFERENCES abdm_consents(id),
    status VARCHAR(50) NOT NULL, -- 'requested', 'processing', 'completed', 'failed'
    hip_ids JSONB, -- Array of HIP IDs that will provide data
    data_push_url TEXT,
    encryption_key JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_abdm_data_requests_consent_id ON abdm_data_requests(consent_id);
```

### 4.5 Audit & Compliance Tables

```sql
-- Audit Log (for compliance and security)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- 'view_patient', 'create_prescription', etc.
    resource_type VARCHAR(50), -- 'patient', 'prescription', 'fhir_resource'
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_status INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Partition by month for performance
CREATE TABLE audit_logs_y2026m02 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

---

## 5. Security Architecture

### 5.1 Authentication Flow

```
┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
│             │                 │             │                 │             │
│   Client    │ ◄─── TLS 1.3 ───┤ API Gateway │ ◄─── mTLS ──────┤  Services   │
│             │                 │   (Kong)    │                 │  (FastAPI)  │
└─────────────┘                 └─────────────┘                 └─────────────┘
                                        │
                                        ▼
                                ┌──────────────┐
                                │ Auth Service │
                                │  (JWT/RBAC)  │
                                └──────────────┘
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                  ┌──────────┐   ┌──────────┐   ┌──────────┐
                  │   HPR    │   │   ABHA   │   │  Redis   │
                  │   API    │   │   API    │   │  Cache   │
                  └──────────┘   └──────────┘   └──────────┘
```

### 5.2 Encryption Standards

```yaml
Data in Transit:
  - TLS 1.3 for all external communication
  - mTLS for inter-service communication
  - Certificate rotation every 90 days

Data at Rest:
  - Database: AES-256 encryption (PostgreSQL pgcrypto)
  - File Storage: S3 SSE-KMS (AWS managed keys)
  - Backups: Encrypted with AWS KMS or Azure Key Vault

ABDM Data Exchange:
  - ECDH (Elliptic Curve Diffie-Hellman) for key exchange
  - AES-256-GCM for payload encryption
  - Per-transaction ephemeral keys
```

### 5.3 Access Control (RBAC)

```python
# Role-Based Permissions Matrix

PERMISSIONS = {
    "doctor_allopathy": [
        "view_patient_records",
        "create_soap_notes",
        "prescribe_allopathic",
        "prescribe_schedule_h",
        "prescribe_schedule_x",  # Requires additional verification
        "order_lab_tests",
        "view_fhir_resources"
    ],
    "doctor_ayurveda": [
        "view_patient_records",
        "create_soap_notes",
        "prescribe_ayush",
        "assess_prakriti",
        "create_panchakarma_plan",
        "view_fhir_resources"
    ],
    "nurse": [
        "view_patient_records",
        "record_vitals",
        "view_prescriptions"
    ],
    "admin": [
        "manage_users",
        "view_audit_logs",
        "system_configuration"
    ]
}

# System Segregation Rules
def can_prescribe(doctor, medication):
    if medication.schedule in ["H", "X"] and doctor.system != "allopathy":
        return False, "Only allopathic doctors can prescribe Schedule H/X drugs"
    
    if medication.type == "ayush" and doctor.system not in ["ayurveda", "homeopathy", "unani"]:
        return False, "Only AYUSH doctors can prescribe traditional medicines"
    
    return True, None
```

### 5.4 Data Residency Compliance

```yaml
Infrastructure Requirements:
  - Cloud Region: AWS Mumbai (ap-south-1) or Azure Central India
  - Database: RDS PostgreSQL in India region
  - File Storage: S3 buckets with India-only replication
  - AI Processing: SageMaker/Azure ML endpoints in India
  - No cross-border data transfer except for:
      - Encrypted backups to secondary India region
      - Aggregated, anonymized analytics (if permitted)

MeitY Empanelled Providers (as of 2026):
  - AWS India
  - Microsoft Azure India
  - Google Cloud India
  - Tata Communications
  - NIC (National Informatics Centre)
```

---

## 6. AI/ML Pipeline Architecture

### 6.1 Medical Scribe Pipeline

```
┌───────────────────────────────────────────────────────────────┐
│                    AUDIO INPUT (WebSocket)                     │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│         Speech-to-Text (Whisper Large v3 - Medical)           │
│  - Custom fine-tuned on Indian medical conversations          │
│  - Hindi/English code-switching support                       │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│              Medical Entity Extraction (NER)                   │
│  - scispaCy + MedCAT                                          │
│  - Entities: Symptoms, Diagnoses, Medications, Vitals         │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│            SOAP Note Generation (Medical LLM)                  │
│  - Fine-tuned Llama 3.1 70B (medical instruction tuning)      │
│  - Structured output: Subjective, Objective, Assessment, Plan │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│         Clinical Coding (SNOMED-CT / LOINC / NAMASTE)         │
│  - Automated ICD-10 / SNOMED-CT mapping                       │
│  - AYUSH: NAMASTE code assignment                             │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│              Real-time Validation & Suggestions                │
│  - Drug interaction checking                                  │
│  - Dosage validation                                          │
│  - Clinical decision support                                  │
└───────────────────────────────────────────────────────────────┘
```

### 6.2 OCR & Document Processing Pipeline

```
┌───────────────────────────────────────────────────────────────┐
│              Document Upload (PDF/Image)                       │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│        Document Classification (CNN - ResNet)                  │
│  - Lab Report, Prescription, Imaging Report, etc.             │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│         OCR Processing (AWS Textract / Azure DI)               │
│  - Layout detection                                           │
│  - Table extraction                                           │
│  - Handwriting recognition                                    │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│           Medical Transformer (Post-Processing)                │
│  - Convert raw text to structured data                        │
│  - "BP 130/90" → FHIR Observation resource                    │
│  - "HbA1c 7.8%" → LOINC coded observation                     │
└─────────────────────────┬─────────────────────────────────────┘
                          ▼
┌───────────────────────────────────────────────────────────────┐
│              FHIR Resource Creation                            │
│  - Observation, Condition, MedicationStatement, etc.          │
│  - Stored in PostgreSQL as JSONB                              │
└───────────────────────────────────────────────────────────────┘
```

### 6.3 Drug Interaction Detection

```python
# Multi-source interaction checking

class InteractionChecker:
    def __init__(self):
        self.allopathic_db = RxNormAPI()
        self.ayush_db = NAMASTEPortal()
        self.herb_drug_db = NaturalMedicinesDatabase()
        self.custom_model = load_model("herb_drug_interaction_model.pkl")
    
    async def check_interactions(self, medications, ayush_meds, patient_conditions):
        interactions = []
        
        # 1. Allopathic drug-drug interactions (RxNorm API)
        allopathic_interactions = await self.allopathic_db.check_interactions(
            [med.rxnorm_code for med in medications]
        )
        
        # 2. Herb-drug interactions (custom ML model + knowledge base)
        for herb in ayush_meds:
            for drug in medications:
                # Check knowledge base first
                kb_interaction = self.herb_drug_db.query(herb.name, drug.generic)
                
                # If not in KB, use ML model
                if not kb_interaction:
                    ml_prediction = self.custom_model.predict(
                        herb_features=herb.extract_features(),
                        drug_features=drug.extract_features()
                    )
                    if ml_prediction.probability > 0.7:
                        interactions.append(ml_prediction.to_interaction())
                else:
                    interactions.append(kb_interaction)
        
        # 3. Contraindication checking against patient conditions
        for med in medications + ayush_meds:
            for condition in patient_conditions:
                contraindication = self.check_contraindication(med, condition)
                if contraindication:
                    interactions.append(contraindication)
        
        return interactions
```

---

## 7. Deployment Architecture

### 7.1 Kubernetes Cluster Configuration

```yaml
# Production Kubernetes Setup (AWS EKS / Azure AKS)

apiVersion: v1
kind: Namespace
metadata:
  name: integmed-prod

---
# API Gateway (Kong)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kong-gateway
  namespace: integmed-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kong
  template:
    metadata:
      labels:
        app: kong
    spec:
      containers:
      - name: kong
        image: kong:3.5
        ports:
        - containerPort: 8000
          name: proxy
        - containerPort: 8443
          name: proxy-ssl
        env:
        - name: KONG_DATABASE
          value: postgres
        - name: KONG_PG_HOST
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: host

---
# FastAPI Application
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clinical-service
  namespace: integmed-prod
spec:
  replicas: 5
  selector:
    matchLabels:
      app: clinical-service
  template:
    metadata:
      labels:
        app: clinical-service
    spec:
      containers:
      - name: fastapi
        image: integmed/clinical-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
# AI Scribe Service (GPU-enabled)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-scribe-service
  namespace: integmed-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-scribe
  template:
    metadata:
      labels:
        app: ai-scribe
    spec:
      nodeSelector:
        gpu: nvidia-t4
      containers:
      - name: ai-scribe
        image: integmed/ai-scribe:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "8Gi"
            cpu: "4000m"
```

### 7.2 Infrastructure as Code (Terraform)

```hcl
# AWS EKS Cluster Configuration

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "integmed-prod"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # India data residency
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = false

  eks_managed_node_groups = {
    general = {
      min_size     = 3
      max_size     = 10
      desired_size = 5

      instance_types = ["t3.xlarge"]
      capacity_type  = "SPOT"
    }

    gpu_nodes = {
      min_size     = 1
      max_size     = 5
      desired_size = 2

      instance_types = ["g4dn.xlarge"] # NVIDIA T4 GPU
      capacity_type  = "ON_DEMAND"
    }
  }

  # Enable IRSA for service accounts
  enable_irsa = true
}

# RDS PostgreSQL
module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "integmed-prod-db"

  engine               = "postgres"
  engine_version       = "16.1"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 500

  db_name  = "integmed"
  username = "integmed_admin"
  port     = 5432

  # High availability
  multi_az               = true
  backup_retention_period = 30
  backup_window          = "03:00-06:00"
  maintenance_window     = "Mon:00:00-Mon:03:00"

  # Encryption
  storage_encrypted = true
  kms_key_id       = aws_kms_key.rds.arn

  # Data residency: India only
  availability_zone = "ap-south-1a"

  # Performance Insights
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = true
}

# ElastiCache Redis
module "redis" {
  source = "terraform-aws-modules/elasticache/aws"

  cluster_id           = "integmed-prod-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.r6g.large"
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"

  # High availability
  automatic_failover_enabled = true

  # Encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  # Data residency
  availability_zones = ["ap-south-1a", "ap-south-1b"]
}
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Week 1-2: Infrastructure Setup**
- [ ] AWS/Azure account setup (India regions)
- [ ] Kubernetes cluster provisioning
- [ ] Database setup (PostgreSQL + Redis)
- [ ] CI/CD pipeline (GitHub Actions / GitLab CI)
- [ ] Monitoring stack (Prometheus + Grafana)

**Week 3-4: Core Authentication**
- [ ] HPR integration (doctor authentication)
- [ ] ABHA integration (patient authentication)
- [ ] JWT token management
- [ ] RBAC implementation
- [ ] Audit logging setup

### Phase 2: Clinical Workflows (Weeks 5-10)

**Week 5-6: Patient & Encounter Management**
- [ ] Patient registration API
- [ ] Encounter creation/management
- [ ] SOAP note structure
- [ ] Basic UI (Next.js setup)

**Week 7-8: ABDM Integration**
- [ ] Discovery API implementation
- [ ] Consent flow
- [ ] Health data fetch
- [ ] FHIR resource parsing & storage
- [ ] Health Graph/Timeline UI

**Week 9-10: Prescription System**
- [ ] Prescription drafting API
- [ ] Shorthand expansion (AI-powered)
- [ ] NMC compliance validation
- [ ] Generic-first enforcement
- [ ] QR code generation
- [ ] Electronic signature

### Phase 3: AI/ML Integration (Weeks 11-16)

**Week 11-12: Medical Scribe**
- [ ] Whisper model fine-tuning (medical vocabulary)
- [ ] Real-time transcription (WebSocket)
- [ ] Medical NER (entity extraction)
- [ ] SOAP note generation

**Week 13-14: Document Processing**
- [ ] OCR pipeline (AWS Textract integration)
- [ ] Document classification
- [ ] FHIR resource generation from OCR
- [ ] Bulk upload UI

**Week 15-16: Drug Interaction System**
- [ ] RxNorm integration
- [ ] Herb-drug interaction database
- [ ] ML model for novel interactions
- [ ] Real-time interaction checking UI

### Phase 4: AYUSH Integration (Weeks 17-20)

**Week 17-18: NAMASTE Portal**
- [ ] NAMASTE API integration
- [ ] Prakriti/Vikriti assessment
- [ ] Nadi pulse documentation
- [ ] Ayurvedic formulation database

**Week 19-20: Cross-System Features**
- [ ] Integrated Health Graph (Allopathy + AYUSH)
- [ ] Herb-drug interaction UI alerts
- [ ] System segregation enforcement
- [ ] Dual prescription templates

### Phase 5: Testing & Compliance (Weeks 21-24)

**Week 21-22: Security Audit**
- [ ] Penetration testing
- [ ] VAPT (Vulnerability Assessment)
- [ ] Data encryption verification
- [ ] ABDM compliance certification

**Week 23-24: Clinical Validation**
- [ ] Pilot with 5 clinics (mixed Allopathy + AYUSH)
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Load testing (1000 concurrent users)

### Phase 6: Production Launch (Week 25+)

**Week 25-26: Pre-Production**
- [ ] Production database migration
- [ ] Backup & disaster recovery testing
- [ ] Documentation finalization
- [ ] Training materials

**Week 27: Go-Live**
- [ ] Staged rollout (10 clinics → 50 clinics → 200 clinics)
- [ ] 24/7 monitoring
- [ ] On-call engineering support
- [ ] Hotfix deployment readiness

---

## 9. Compliance Checklist

### 9.1 ABDM Compliance

- [x] HPR authentication integration
- [x] ABHA authentication integration
- [x] Discovery API implementation
- [x] Consent management (M1 flow)
- [x] Health data fetch with encryption
- [x] FHIR R4/R5 support
- [x] Digital health locker push
- [ ] ABDM sandbox testing certification
- [ ] Production gateway approval

### 9.2 NMC (National Medical Commission) Compliance

- [x] Generic name in CAPITAL letters
- [x] Brand name as "Suggested Brand" (optional)
- [x] Doctor's full qualification on prescription
- [x] Registration number display
- [x] Electronic signature (IT Act 2000 compliant)
- [x] System segregation (MBBS cannot prescribe AYUSH, BAMS cannot prescribe Schedule H/X)
- [ ] Prescription format review by legal team

### 9.3 Data Privacy & Security

- [x] Data residency in India
- [x] AES-256 encryption at rest
- [x] TLS 1.3 for data in transit
- [x] RBAC with least privilege
- [x] Audit logs (retention: 7 years)
- [x] Patient consent for data sharing
- [ ] ISO 27001 certification (target: Month 6)
- [ ] HIPAA-equivalent compliance (if international expansion)

### 9.4 AYUSH Compliance

- [x] NAMASTE Portal integration
- [x] Prakriti/Vikriti documentation
- [x] Ayurvedic Pharmacopoeia of India (API) reference
- [x] Contraindication checking for herbs
- [ ] Ministry of AYUSH registration
- [ ] Traditional medicine practitioner verification

---

## 10. Monitoring & Observability

### 10.1 Metrics Collection

```yaml
Metrics Stack:
  - Prometheus: Time-series metrics
  - Grafana: Visualization dashboards
  - Loki: Log aggregation
  - Tempo: Distributed tracing

Key Metrics:
  API Performance:
    - Request latency (p50, p95, p99)
    - Error rate (5xx errors)
    - Throughput (requests/second)
  
  Database:
    - Connection pool utilization
    - Query duration
    - Slow query count
  
  AI/ML:
    - Transcription accuracy
    - Entity extraction F1 score
    - Interaction detection precision
  
  Business Metrics:
    - Prescriptions created per day
    - ABDM data fetch success rate
    - Average encounter duration
```

### 10.2 Alerting

```yaml
Critical Alerts (PagerDuty):
  - API error rate > 5% (5min window)
  - Database connection pool > 90%
  - ABDM gateway downtime
  - Prescription signing failures
  - Data encryption errors

Warning Alerts (Slack):
  - API latency p95 > 2s
  - Redis cache hit rate < 80%
  - AI scribe accuracy < 90%
  - OCR processing backlog > 100 files
```

---

## Appendix A: Technology Justification Summary

| Component | Choice | Alternative Considered | Reason |
|-----------|--------|----------------------|--------|
| Backend | FastAPI | Django, Flask | Async support, Pydantic validation, FHIR libraries |
| Frontend | Next.js 14 | React SPA, Vue | Server components, SEO, real-time support |
| Database | PostgreSQL 16 | MongoDB, MySQL | JSONB for FHIR, ACID compliance, TimescaleDB |
| Cache | Redis 7 | Memcached | Pub/Sub for real-time, data structures |
| AI/ML | Python ecosystem | JavaScript/TypeScript | Medical NLP libraries, model availability |
| Cloud | AWS India | Azure, GCP | MeitY empanelment, mature services, PrivateLink |
| Container Orchestration | Kubernetes | Docker Swarm, ECS | Industry standard, GPU support, auto-scaling |

---

## Appendix B: API Rate Limits

| Endpoint Category | Authenticated | Unauthenticated | Burst Limit |
|------------------|--------------|----------------|-------------|
| Authentication | 10/min | 5/min | 20 |
| ABDM APIs | 100/min | N/A | 200 |
| Prescription | 50/min | N/A | 100 |
| FHIR Resources | 200/min | N/A | 500 |
| AI Scribe (WebSocket) | 5 concurrent | N/A | 10 |
| Document Upload | 20/min | N/A | 30 |

---

## Appendix C: Disaster Recovery Plan

```yaml
Backup Strategy:
  Database:
    - Automated daily backups (retained 30 days)
    - Point-in-time recovery (up to 35 days)
    - Cross-region replication (Mumbai → Hyderabad)
  
  File Storage:
    - S3 versioning enabled
    - Cross-region replication
    - Glacier archival after 90 days

Recovery Time Objective (RTO): 4 hours
Recovery Point Objective (RPO): 1 hour

Disaster Scenarios:
  1. Database failure:
     - Promote read replica to primary
     - Update DNS/connection strings
     - Verify data integrity
     - ETA: 30 minutes
  
  2. Region outage:
     - Failover to secondary region (Hyderabad)
     - Route 53 health check automatic failover
     - ETA: 2 hours
  
  3. Complete data center loss:
     - Restore from latest backup
     - Provision new infrastructure
     - ETA: 4 hours
```

---

**Document End**

---

**Next Steps:**
1. Review and approve technical architecture
2. Set up development environment
3. Begin Phase 1 implementation
4. Schedule weekly architecture review meetings
5. Prepare for ABDM sandbox testing application

**Contact:**
For questions or clarifications on this architecture document, please contact the engineering team.
