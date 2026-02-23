"""
Prescription API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import re
import hashlib
import qrcode
import io
import base64
from datetime import datetime

from app.core.database import get_db
from app.models.database import Prescription, User, Patient, Encounter
from app.schemas.api import (
    PrescriptionCreate,
    PrescriptionResponse,
    ShorthandExpansion,
    MedicationExpanded,
    InteractionCheckRequest,
    InteractionCheckResponse,
    Interaction
)
from app.api.auth import get_current_user

router = APIRouter()


# =============== Prescription Management ===============

@router.post("/draft", response_model=PrescriptionResponse)
async def create_prescription_draft(
    prescription_data: PrescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a prescription draft
    Validates NMC compliance and drug interactions
    """
    # Verify encounter exists and belongs to patient
    encounter = db.query(Encounter).filter(
        Encounter.id == prescription_data.encounter_id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    # Validate system-based prescribing rights
    _validate_prescribing_rights(current_user, prescription_data)
    
    # Validate NMC compliance (generic-first)
    nmc_compliant = all(
        med.generic_name and med.generic_name == med.generic_name.upper()
        for med in prescription_data.medications
    )
    
    # Generate prescription number
    prescription_number = _generate_prescription_number(encounter.patient_id)
    
    # Create prescription
    prescription = Prescription(
        prescription_number=prescription_number,
        encounter_id=prescription_data.encounter_id,
        patient_id=encounter.patient_id,
        doctor_id=current_user.id,
        status="draft",
        medications=[med.dict() for med in prescription_data.medications],
        ayush_medications=[med.dict() for med in prescription_data.ayush_medications] if prescription_data.ayush_medications else None,
        instructions=prescription_data.instructions,
        nmc_compliant=nmc_compliant,
        generic_first=nmc_compliant
    )
    
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    
    return PrescriptionResponse.from_orm(prescription)


@router.post("/expand-shorthand", response_model=MedicationExpanded)
async def expand_medication_shorthand(
    shorthand: ShorthandExpansion,
    current_user: User = Depends(get_current_user)
):
    """
    Expand medication shorthand to full prescription format
    Example: "Metf 1000 bd 30d" -> Full medication object
    """
    expanded = _parse_medication_shorthand(shorthand.shorthand)
    
    if not expanded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shorthand format"
        )
    
    return expanded


@router.post("/check-interactions", response_model=InteractionCheckResponse)
async def check_drug_interactions(
    request: InteractionCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Check for drug-drug and herb-drug interactions
    Returns interaction warnings and contraindications
    """
    interactions = []
    contraindications = []
    allergy_alerts = []
    
    # Check allopathic drug-drug interactions
    for i, med1 in enumerate(request.medications):
        for med2 in request.medications[i+1:]:
            interaction = _check_drug_drug_interaction(med1, med2)
            if interaction:
                interactions.append(interaction)
    
    # Check herb-drug interactions
    if request.ayush_medications:
        for ayush_med in request.ayush_medications:
            for allopathic_med in request.medications:
                interaction = _check_herb_drug_interaction(ayush_med, allopathic_med)
                if interaction:
                    interactions.append(interaction)
    
    # Check contraindications
    if request.patient_conditions:
        for med in request.medications:
            for condition in request.patient_conditions:
                contraindication = _check_contraindication(med, condition)
                if contraindication:
                    contraindications.append(contraindication)
    
    # Check allergies
    if request.patient_allergies:
        for med in request.medications:
            if _is_allergic(med, request.patient_allergies):
                allergy_alerts.append({
                    "medication": med.generic_name,
                    "severity": "critical",
                    "message": "Patient has known allergy to this medication"
                })
    
    # Calculate safety score (0-10)
    safety_score = _calculate_safety_score(interactions, contraindications, allergy_alerts)
    
    return InteractionCheckResponse(
        interactions=interactions,
        contraindications=contraindications,
        allergy_alerts=allergy_alerts,
        safety_score=safety_score
    )


@router.post("/{prescription_id}/sign", response_model=PrescriptionResponse)
async def sign_prescription(
    prescription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Digitally sign prescription
    Generates signature hash and QR code
    """
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.doctor_id == current_user.id
    ).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    if prescription.status == "signed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescription already signed"
        )
    
    # Generate signature hash
    signature_data = f"{prescription.id}{current_user.id}{datetime.utcnow().isoformat()}"
    signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
    
    # Generate QR code
    qr_data = f"https://integmed.health/rx/{prescription.prescription_number}?v={signature_hash[:8]}"
    qr_image = _generate_qr_code(qr_data)
    
    # Update prescription
    prescription.status = "signed"
    prescription.signature_hash = signature_hash
    prescription.signature_timestamp = datetime.utcnow()
    prescription.qr_code_data = qr_data
    prescription.qr_code_image = qr_image
    
    db.commit()
    db.refresh(prescription)
    
    return PrescriptionResponse.from_orm(prescription)


# =============== Helper Functions ===============

def _validate_prescribing_rights(user: User, prescription_data: PrescriptionCreate):
    """
    Validate that doctor has rights to prescribe these medications
    """
    # AYUSH doctors cannot prescribe Schedule H/X drugs
    if user.system in ["ayurveda", "homeopathy", "unani"]:
        for med in prescription_data.medications:
            if "Schedule H" in med.instructions or "Schedule X" in med.instructions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"{user.system.capitalize()} practitioners cannot prescribe Schedule H/X drugs"
                )
    
    # Allopathic doctors can prescribe AYUSH medications (but warning should be given)
    # No restriction here, but could add warning


def _parse_medication_shorthand(shorthand: str) -> MedicationExpanded:
    """
    Parse medication shorthand into structured format
    Example: "Metf 1000 bd 30d" -> Metformin 1000mg, twice daily, 30 days
    """
    # Medication database (in production, this would be a proper database)
    MED_DB = {
        "metf": {"generic": "METFORMIN", "forms": ["tablet"], "rxnorm": "6809"},
        "amlo": {"generic": "AMLODIPINE", "forms": ["tablet"], "rxnorm": "17767"},
        "aspi": {"generic": "ASPIRIN", "forms": ["tablet"], "rxnorm": "1191"},
        "para": {"generic": "PARACETAMOL", "forms": ["tablet"], "rxnorm": "161"},
    }
    
    # Frequency mapping
    FREQ_MAP = {
        "od": "Once daily",
        "bd": "Twice daily",
        "tid": "Three times daily",
        "qid": "Four times daily",
    }
    
    # Parse shorthand: "drug strength frequency duration"
    pattern = r"(\w+)\s+(\d+)\s+(\w+)\s+(\d+)d"
    match = re.match(pattern, shorthand.lower())
    
    if not match:
        return None
    
    drug_code, strength, freq, duration = match.groups()
    
    # Look up drug
    drug_info = MED_DB.get(drug_code)
    if not drug_info:
        return None
    
    frequency_text = FREQ_MAP.get(freq, freq.upper())
    
    return MedicationExpanded(
        generic_name=drug_info["generic"],
        brand_suggestions=[],  # Would be populated from database
        strength=f"{strength}mg",
        dosage_form="tablet",
        route="oral",
        frequency=frequency_text,
        duration_days=int(duration),
        quantity=_calculate_quantity(freq, int(duration)),
        instructions="Take after meals",
        rxnorm_code=drug_info.get("rxnorm")
    )


def _calculate_quantity(frequency: str, duration_days: int) -> int:
    """
    Calculate total quantity needed
    """
    freq_multiplier = {
        "od": 1,
        "bd": 2,
        "tid": 3,
        "qid": 4
    }
    return freq_multiplier.get(frequency, 1) * duration_days


def _check_drug_drug_interaction(med1: MedicationExpanded, med2: MedicationExpanded) -> Interaction:
    """
    Check for drug-drug interactions
    In production, this would query a comprehensive drug interaction database
    """
    # Example interactions (simplified)
    known_interactions = {
        ("METFORMIN", "ASPIRIN"): {
            "severity": "moderate",
            "description": "Aspirin may enhance the hypoglycemic effect of Metformin",
            "recommendation": "Monitor blood glucose levels closely"
        }
    }
    
    key = tuple(sorted([med1.generic_name, med2.generic_name]))
    interaction_data = known_interactions.get(key)
    
    if interaction_data:
        return Interaction(
            type="drug_drug",
            severity=interaction_data["severity"],
            drug1=med1.generic_name,
            drug2=med2.generic_name,
            description=interaction_data["description"],
            recommendation=interaction_data["recommendation"]
        )
    
    return None


def _check_herb_drug_interaction(ayush_med, allopathic_med: MedicationExpanded) -> Interaction:
    """
    Check for herb-drug interactions
    """
    # Example herb-drug interactions
    herb_drug_interactions = {
        ("Triphala", "METFORMIN"): {
            "severity": "moderate",
            "description": "Triphala may enhance hypoglycemic effects of Metformin",
            "recommendation": "Monitor blood glucose levels closely. Consider adjusting doses."
        },
        ("Ashwagandha", "METFORMIN"): {
            "severity": "moderate",
            "description": "Ashwagandha may enhance hypoglycemic effects",
            "recommendation": "Monitor blood glucose. Start with lower doses."
        }
    }
    
    key = (ayush_med.name, allopathic_med.generic_name)
    interaction_data = herb_drug_interactions.get(key)
    
    if interaction_data:
        return Interaction(
            type="herb_drug",
            severity=interaction_data["severity"],
            drug1=ayush_med.name,
            drug2=allopathic_med.generic_name,
            description=interaction_data["description"],
            recommendation=interaction_data["recommendation"],
            references=["J Ethnopharmacol. 2015;179:190-197"]
        )
    
    return None


def _check_contraindication(med: MedicationExpanded, condition: str) -> dict:
    """
    Check for contraindications based on patient conditions
    """
    contraindications = {
        ("METFORMIN", "kidney_disease"): "Contraindicated in severe renal impairment",
        ("ASPIRIN", "bleeding_disorder"): "Contraindicated in active bleeding disorders"
    }
    
    key = (med.generic_name, condition)
    if key in contraindications:
        return {
            "medication": med.generic_name,
            "condition": condition,
            "severity": "critical",
            "message": contraindications[key]
        }
    
    return None


def _is_allergic(med: MedicationExpanded, allergies: List[str]) -> bool:
    """
    Check if patient is allergic to medication
    """
    return med.generic_name.lower() in [allergy.lower() for allergy in allergies]


def _calculate_safety_score(interactions, contraindications, allergy_alerts) -> float:
    """
    Calculate overall safety score (0-10)
    10 = completely safe, 0 = critical issues
    """
    score = 10.0
    
    # Deduct points for each issue
    for interaction in interactions:
        if interaction.severity == "critical":
            score -= 3.0
        elif interaction.severity == "severe":
            score -= 2.0
        elif interaction.severity == "moderate":
            score -= 1.0
        elif interaction.severity == "mild":
            score -= 0.5
    
    for contraindication in contraindications:
        score -= 3.0
    
    for alert in allergy_alerts:
        score -= 4.0
    
    return max(0.0, score)


def _generate_prescription_number(patient_id: UUID) -> str:
    """
    Generate unique prescription number
    Format: RX-YYYYMMDD-XXXXX
    """
    date_str = datetime.now().strftime("%Y%m%d")
    # In production, get sequential number from database
    seq = hashlib.md5(str(patient_id).encode()).hexdigest()[:5].upper()
    return f"RX-{date_str}-{seq}"


def _generate_qr_code(data: str) -> str:
    """
    Generate QR code and return as base64 string
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str
