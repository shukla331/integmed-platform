"""
SQLAlchemy Database Models
"""
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Date, Text, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """
    Doctors, Nurses, and Admin staff
    """
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    hpr_id = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    system = Column(String(20), nullable=False)  # 'allopathy', 'ayurveda', 'homeopathy', 'unani'
    qualification = Column(String(255), nullable=True)
    registration_number = Column(String(100), unique=True, nullable=True)
    registration_council = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False)  # 'doctor', 'nurse', 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    encounters = relationship("Encounter", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
    consents = relationship("ABDMConsent", back_populates="doctor")


class Patient(Base):
    """
    Patient records
    """
    __tablename__ = "patients"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    abha_number = Column(String(17), unique=True, nullable=True, index=True)
    abha_address = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    mobile = Column(String(15), nullable=True, index=True)
    email = Column(String(255), nullable=True)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    year_of_birth = Column(Integer, nullable=True)
    address = Column(JSONB, nullable=True)
    emergency_contact = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    fhir_resources = relationship("FHIRResource", back_populates="patient", cascade="all, delete-orphan")
    consents = relationship("ABDMConsent", back_populates="patient", cascade="all, delete-orphan")


class Clinic(Base):
    """
    Clinic/Hospital information
    """
    __tablename__ = "clinics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    hip_id = Column(String(100), unique=True, nullable=True)  # ABDM HIP ID
    address = Column(JSONB, nullable=True)
    phone = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    encounters = relationship("Encounter", back_populates="clinic")


class Encounter(Base):
    """
    Clinical visits/consultations
    """
    __tablename__ = "encounters"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    clinic_id = Column(PG_UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=True)
    encounter_type = Column(String(50), nullable=False)  # 'opd', 'emergency', 'followup'
    status = Column(String(50), nullable=False)  # 'scheduled', 'in_progress', 'completed'
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    chief_complaint = Column(Text, nullable=True)
    soap_note = Column(JSONB, nullable=True)  # Full SOAP structure
    ayush_assessment = Column(JSONB, nullable=True)  # Prakriti, Vikriti, Nadi
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="encounters")
    doctor = relationship("User", back_populates="encounters")
    clinic = relationship("Clinic", back_populates="encounters")
    prescriptions = relationship("Prescription", back_populates="encounter", cascade="all, delete-orphan")
    fhir_resources = relationship("FHIRResource", back_populates="encounter", cascade="all, delete-orphan")


class Prescription(Base):
    """
    Medical prescriptions (Allopathic + AYUSH)
    """
    __tablename__ = "prescriptions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    prescription_number = Column(String(50), unique=True, nullable=False, index=True)
    encounter_id = Column(PG_UUID(as_uuid=True), ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)  # 'draft', 'signed', 'dispensed', 'cancelled'
    medications = Column(JSONB, nullable=False)  # Array of medication objects
    ayush_medications = Column(JSONB, nullable=True)  # Array of AYUSH medications
    instructions = Column(Text, nullable=True)
    
    # Digital Signature
    signature_hash = Column(String(255), nullable=True)
    signature_timestamp = Column(DateTime(timezone=True), nullable=True)
    signature_certificate = Column(Text, nullable=True)
    
    # QR Code
    qr_code_data = Column(Text, nullable=True)
    qr_code_image = Column(Text, nullable=True)  # Base64 encoded
    
    # ABDM Integration
    abdm_pushed = Column(Boolean, default=False)
    abdm_push_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Compliance
    nmc_compliant = Column(Boolean, default=True)
    generic_first = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    encounter = relationship("Encounter", back_populates="prescriptions")
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("User", back_populates="prescriptions")


class FHIRResource(Base):
    """
    FHIR resources (Observations, Conditions, etc.)
    """
    __tablename__ = "fhir_resources"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False)
    patient_id = Column(PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True)
    encounter_id = Column(PG_UUID(as_uuid=True), ForeignKey("encounters.id", ondelete="CASCADE"), nullable=True)
    
    # Full FHIR resource
    resource = Column(JSONB, nullable=False)
    
    # Extracted fields for querying
    category = Column(String(100), nullable=True, index=True)
    code = Column(String(100), nullable=True, index=True)
    effective_date = Column(Date, nullable=True, index=True)
    value_numeric = Column(Numeric, nullable=True)
    value_text = Column(Text, nullable=True)
    
    # Source tracking
    source = Column(String(100), nullable=True)
    source_system = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="fhir_resources")
    encounter = relationship("Encounter", back_populates="fhir_resources")


class ABDMConsent(Base):
    """
    ABDM consent requests and artifacts
    """
    __tablename__ = "abdm_consents"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    consent_request_id = Column(String(255), unique=True, nullable=False, index=True)
    patient_id = Column(PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    purpose = Column(String(100), nullable=False)
    hi_types = Column(JSONB, nullable=False)
    date_range = Column(JSONB, nullable=False)
    status = Column(String(50), nullable=False, index=True)
    consent_artifact = Column(JSONB, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="consents")
    doctor = relationship("User", back_populates="consents")
    data_requests = relationship("ABDMDataRequest", back_populates="consent", cascade="all, delete-orphan")


class ABDMDataRequest(Base):
    """
    ABDM health information fetch requests
    """
    __tablename__ = "abdm_data_requests"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id = Column(String(255), unique=True, nullable=False, index=True)
    consent_id = Column(PG_UUID(as_uuid=True), ForeignKey("abdm_consents.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    hip_ids = Column(JSONB, nullable=True)
    data_push_url = Column(Text, nullable=True)
    encryption_key = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    consent = relationship("ABDMConsent", back_populates="data_requests")


class AuditLog(Base):
    """
    Audit trail for compliance and security
    """
    __tablename__ = "audit_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(PG_UUID(as_uuid=True), nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_data = Column(JSONB, nullable=True)
    response_status = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
