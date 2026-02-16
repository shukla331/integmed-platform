"""
Patient Management and Clinical API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Patient, Encounter, FHIRResource
from app.schemas.api import (
    PatientCreate,
    PatientResponse,
    EncounterCreate,
    EncounterUpdate,
    EncounterResponse,
    HealthTimelineResponse,
    TimelineEvent
)
from app.api.auth import get_current_user
from app.models.database import User

# Patient Router
patients_router = APIRouter()


@patients_router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a new patient
    """
    # Check if ABHA already exists
    if patient_data.abha_number:
        existing = db.query(Patient).filter(
            Patient.abha_number == patient_data.abha_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this ABHA number already exists"
            )
    
    patient = Patient(**patient_data.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    return PatientResponse.from_orm(patient)


@patients_router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient details
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return PatientResponse.from_orm(patient)


# Encounter Router
encounters_router = APIRouter()


@encounters_router.post("/", response_model=EncounterResponse)
async def create_encounter(
    encounter_data: EncounterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new clinical encounter
    """
    encounter = Encounter(
        **encounter_data.dict(),
        doctor_id=current_user.id,
        status="in_progress"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    
    return EncounterResponse.from_orm(encounter)


@encounters_router.patch("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: UUID,
    encounter_update: EncounterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update encounter (add SOAP note, change status)
    """
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.doctor_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    # Update fields
    update_data = encounter_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "soap_note" or field == "ayush_assessment":
            # Convert Pydantic model to dict for JSONB storage
            value = value.dict() if value else None
        setattr(encounter, field, value)
    
    db.commit()
    db.refresh(encounter)
    
    return EncounterResponse.from_orm(encounter)


# Clinical Router
clinical_router = APIRouter()


@clinical_router.get("/health-graph/{patient_id}", response_model=HealthTimelineResponse)
async def get_health_timeline(
    patient_id: UUID,
    start_date: datetime = None,
    end_date: datetime = None,
    include_wearables: bool = True,
    include_ayush: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get integrated health timeline (Allopathy + AYUSH + Wearables)
    """
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=365)
    
    timeline_events = []
    
    # Get encounters
    encounters = db.query(Encounter).filter(
        Encounter.patient_id == patient_id,
        Encounter.start_time >= start_date,
        Encounter.start_time <= end_date
    ).order_by(Encounter.start_time.desc()).all()
    
    for encounter in encounters:
        event_type = "ayush" if encounter.ayush_assessment else "allopathic"
        
        event = TimelineEvent(
            date=encounter.start_time,
            type=event_type,
            category="consultation",
            facility=f"Dr. {encounter.doctor.name}",
            data={
                "encounter_id": str(encounter.id),
                "type": encounter.encounter_type,
                "chief_complaint": encounter.chief_complaint,
                "soap_note": encounter.soap_note,
                "ayush_assessment": encounter.ayush_assessment
            }
        )
        timeline_events.append(event)
    
    # Get FHIR resources (labs, observations)
    fhir_resources = db.query(FHIRResource).filter(
        FHIRResource.patient_id == patient_id,
        FHIRResource.effective_date >= start_date.date(),
        FHIRResource.effective_date <= end_date.date()
    ).all()
    
    for resource in fhir_resources:
        event = TimelineEvent(
            date=datetime.combine(resource.effective_date, datetime.min.time()),
            type="allopathic",
            category=resource.category or "observation",
            facility=resource.source_system,
            data={
                "resource_type": resource.resource_type,
                "code": resource.code,
                "value_numeric": float(resource.value_numeric) if resource.value_numeric else None,
                "value_text": resource.value_text,
                "resource": resource.resource
            }
        )
        timeline_events.append(event)
    
    # TODO: Add wearable data if include_wearables is True
    # Query wearable_data table and aggregate
    
    # Sort timeline by date
    timeline_events.sort(key=lambda x: x.date, reverse=True)
    
    # Generate summary
    summary = {
        "total_events": len(timeline_events),
        "last_visit": encounters[0].start_time if encounters else None,
        "chronic_conditions": [],  # Extract from assessment
        "current_medications": 0,  # Count active prescriptions
        "allergy_alerts": []
    }
    
    return HealthTimelineResponse(
        patient_id=patient_id,
        timeline=timeline_events,
        summary=summary
    )


# Export routers
router = patients_router
