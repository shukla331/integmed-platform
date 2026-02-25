"""
Pydantic Schemas for API Request/Response Validation
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# Enums
class SystemType(str, Enum):
    ALLOPATHY = "allopathy"
    AYURVEDA = "ayurveda"
    HOMEOPATHY = "homeopathy"
    UNANI = "unani"


class UserRole(str, Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"


class EncounterType(str, Enum):
    OPD = "opd"
    EMERGENCY = "emergency"
    FOLLOWUP = "followup"


class EncounterStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PrescriptionStatus(str, Enum):
    DRAFT = "draft"
    SIGNED = "signed"
    DISPENSED = "dispensed"
    CANCELLED = "cancelled"


# =============== Authentication Schemas ===============

class HPRAuthInit(BaseModel):
    mobile: str = Field(..., pattern=r"^\+91\d{10}$")
    purpose: str = "login"


class HPRAuthVerify(BaseModel):
    txn_id: str
    otp: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


# =============== User Schemas ===============

class UserBase(BaseModel):
    name: str
    mobile: str
    email: Optional[EmailStr] = None
    system: SystemType
    qualification: Optional[str] = None
    specialization: Optional[str] = None


class UserCreate(UserBase):
    hpr_id: str
    registration_number: str
    registration_council: str
    role: UserRole


class UserResponse(UserBase):
    id: UUID
    hpr_id: Optional[str]
    registration_number: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============== Patient Schemas ===============

class PatientBase(BaseModel):
    name: str
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    year_of_birth: Optional[int] = None


class PatientCreate(PatientBase):
    abha_number: Optional[str] = None
    abha_address: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, Any]] = None


class PatientResponse(PatientBase):
    id: UUID
    abha_number: Optional[str]
    abha_address: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============== SOAP Note Schemas ===============

class SOAPSubjective(BaseModel):
    chief_complaint: str
    history_present_illness: Optional[str] = None
    review_of_systems: Optional[Dict[str, Any]] = None


class SOAPObjective(BaseModel):
    vitals: Dict[str, Any]
    examination: str
    labs: Optional[List[Dict[str, Any]]] = None


class SOAPAssessment(BaseModel):
    primary_diagnosis: Dict[str, str]
    secondary_diagnoses: Optional[List[Dict[str, str]]] = None


class SOAPPlan(BaseModel):
    medications: List[str]
    investigations: Optional[List[str]] = None
    lifestyle_advice: Optional[str] = None
    followup: Optional[str] = None


class SOAPNote(BaseModel):
    subjective: SOAPSubjective
    objective: SOAPObjective
    assessment: SOAPAssessment
    plan: SOAPPlan


class AyushAssessment(BaseModel):
    prakriti: Optional[str] = None
    vikriti: Optional[str] = None
    nadi_pulse: Optional[Dict[str, Any]] = None
    treatment_plan: Optional[Dict[str, Any]] = None


# =============== Encounter Schemas ===============

class EncounterCreate(BaseModel):
    patient_id: UUID
    encounter_type: EncounterType
    start_time: datetime
    chief_complaint: Optional[str] = None


class EncounterUpdate(BaseModel):
    status: Optional[EncounterStatus] = None
    end_time: Optional[datetime] = None
    soap_note: Optional[SOAPNote] = None
    ayush_assessment: Optional[AyushAssessment] = None


class EncounterResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    clinic_id: Optional[UUID]
    encounter_type: EncounterType
    status: EncounterStatus
    start_time: datetime
    end_time: Optional[datetime]
    chief_complaint: Optional[str]
    soap_note: Optional[Dict[str, Any]]
    ayush_assessment: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# =============== Medication Schemas ===============

class MedicationBase(BaseModel):
    generic_name: str
    brand_suggestions: Optional[List[str]] = None
    strength: str
    dosage_form: str
    route: str = "oral"
    frequency: str
    duration_days: int
    quantity: int
    instructions: Optional[str] = None


class MedicationExpanded(MedicationBase):
    snomed_code: Optional[str] = None
    rxnorm_code: Optional[str] = None


class AyushMedication(BaseModel):
    name: str
    type: str  # churna, vati, tailam, etc.
    dose: str
    frequency: str
    anupana: Optional[str] = None  # Vehicle (milk, water, ghee)
    duration_days: int
    namaste_code: Optional[str] = None


# =============== Prescription Schemas ===============

class PrescriptionCreate(BaseModel):
    encounter_id: UUID
    medications: List[MedicationExpanded]
    ayush_medications: Optional[List[AyushMedication]] = None
    instructions: Optional[str] = None


class ShorthandExpansion(BaseModel):
    """
    Input: "Metf 1000 bd 30d"
    Output: Expanded medication object
    """
    shorthand: str

    @validator('shorthand')
    def validate_shorthand(cls, v):
        # Basic validation - real implementation would parse
        if len(v) < 5:
            raise ValueError('Shorthand too short')
        return v


class PrescriptionResponse(BaseModel):
    id: UUID
    prescription_number: str
    encounter_id: UUID
    patient_id: UUID
    doctor_id: UUID
    status: PrescriptionStatus
    medications: List[Dict[str, Any]]
    ayush_medications: Optional[List[Dict[str, Any]]]
    instructions: Optional[str]
    signature_hash: Optional[str]
    signature_timestamp: Optional[datetime]
    qr_code_data: Optional[str]
    abdm_pushed: bool
    nmc_compliant: bool
    generic_first: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============== Interaction Check Schemas ===============

class InteractionCheckRequest(BaseModel):
    medications: List[MedicationExpanded]
    ayush_medications: Optional[List[AyushMedication]] = None
    patient_conditions: Optional[List[str]] = None
    patient_allergies: Optional[List[str]] = None


class Interaction(BaseModel):
    type: str  # 'drug_drug', 'herb_drug', 'contraindication', 'allergy'
    severity: str  # 'mild', 'moderate', 'severe', 'critical'
    drug1: str
    drug2: Optional[str] = None
    description: str
    recommendation: str
    references: Optional[List[str]] = None


class InteractionCheckResponse(BaseModel):
    interactions: List[Interaction]
    contraindications: List[Dict[str, Any]]
    allergy_alerts: List[Dict[str, Any]]
    safety_score: float = Field(..., ge=0, le=10)


# =============== ABDM Schemas ===============

class ABDMDiscoveryRequest(BaseModel):
    patient_abha: str
    patient_name: str
    patient_gender: Optional[str] = None
    patient_year_of_birth: Optional[int] = None


class ABDMConsentRequest(BaseModel):
    patient_id: UUID
    purpose: str = "CAREMGT"
    hi_types: List[str] = ["Prescription", "DiagnosticReport", "OPConsultation"]
    from_date: datetime
    to_date: datetime
    data_erase_at: datetime


class ABDMConsentResponse(BaseModel):
    consent_request_id: str
    status: str
    created_at: datetime


class ABDMHealthDataFetch(BaseModel):
    consent_id: UUID


# =============== FHIR Resource Schemas ===============

class FHIRResourceCreate(BaseModel):
    resource_type: str
    resource_id: str
    patient_id: Optional[UUID] = None
    encounter_id: Optional[UUID] = None
    resource: Dict[str, Any]  # Full FHIR resource
    category: Optional[str] = None
    code: Optional[str] = None
    effective_date: Optional[date] = None
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    source: Optional[str] = None


class FHIRResourceResponse(FHIRResourceCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# =============== Health Timeline Schemas ===============

class TimelineEvent(BaseModel):
    date: datetime
    type: str  # 'wearable', 'allopathic', 'ayush', 'lab', 'consultation'
    category: str
    facility: Optional[str] = None
    data: Dict[str, Any]


class HealthTimelineResponse(BaseModel):
    patient_id: UUID
    timeline: List[TimelineEvent]
    summary: Dict[str, Any]


# Update forward references
TokenResponse.model_rebuild()
