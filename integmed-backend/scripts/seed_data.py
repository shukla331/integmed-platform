"""
Seed database with demo data
Run: python scripts/seed_data.py
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.database import User, Patient, Clinic, Encounter, Prescription, FHIRResource
import logging

logger = logging.getLogger(__name__)


def seed_database():
    """Seed database with demo data"""
    db = SessionLocal()
    
    try:
        logger.info("🌱 Starting database seeding...")
        
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.warning("⚠️ Database already has data. Skipping seed.")
            return
        
        # 1. Create Demo Clinic
        clinic = Clinic(
            name="Apollo Hospital Mumbai",
            hip_id="APOLLO_MUM_001",
            address={
                "line1": "Parsik Hill Road, Sector 23",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400614",
                "country": "India"
            },
            phone="+912269204040",
            email="info@apollohospitals.com"
        )
        db.add(clinic)
        db.flush()
        
        # 2. Create Demo Doctor (MBBS - Allopathy)
        doctor = User(
            hpr_id="HPR-1234567890",
            name="Dr. Priya Sharma",
            mobile="+919876543210",
            email="priya.sharma@integmed.health",
            system="allopathy",
            qualification="MBBS, MD (Internal Medicine)",
            registration_number="MH/12345/2015",
            registration_council="Maharashtra Medical Council",
            specialization="Internal Medicine",
            role="doctor",
            is_active=True
        )
        db.add(doctor)
        db.flush()
        
        # 3. Create Demo Patients
        patient1 = Patient(
            abha_number="12-3456-7890-1234",
            abha_address="rajesh.kumar@abdm",
            name="Rajesh Kumar",
            mobile="+919123456789",
            email="rajesh.kumar@email.com",
            gender="M",
            year_of_birth=1985,
            address={
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India"
            }
        )
        db.add(patient1)
        
        patient2 = Patient(
            abha_number="12-3456-7890-5678",
            abha_address="priya.mehta@abdm",
            name="Priya Mehta",
            mobile="+919987654321",
            email="priya.mehta@email.com",
            gender="F",
            year_of_birth=1990,
            address={
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India"
            }
        )
        db.add(patient2)
        db.flush()
        
        # 4. Create Encounters
        encounter1 = Encounter(
            patient_id=patient1.id,
            doctor_id=doctor.id,
            clinic_id=clinic.id,
            encounter_type="opd",
            status="completed",
            start_time=datetime.utcnow() - timedelta(days=7),
            end_time=datetime.utcnow() - timedelta(days=7, hours=-1),
            chief_complaint="Persistent fatigue and increased thirst",
            soap_note={
                "subjective": {
                    "complaint": "Fatigue for 2 weeks, increased thirst and urination",
                    "history": "No prior diabetes diagnosis"
                },
                "objective": {
                    "vitals": {
                        "bp": "140/90",
                        "pulse": 78,
                        "temp": 98.6,
                        "weight": 75,
                        "height": 170
                    },
                    "examination": "Patient appears tired, no other abnormalities"
                },
                "assessment": {
                    "diagnosis": "Type 2 Diabetes Mellitus - New onset",
                    "icd_code": "E11"
                },
                "plan": {
                    "medications": ["Metformin 500mg BD"],
                    "investigations": ["HbA1c", "Fasting glucose", "Lipid profile"],
                    "followup": "2 weeks"
                }
            }
        )
        db.add(encounter1)
        
        encounter2 = Encounter(
            patient_id=patient1.id,
            doctor_id=doctor.id,
            clinic_id=clinic.id,
            encounter_type="followup",
            status="completed",
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow() - timedelta(days=1, hours=-0.5),
            chief_complaint="Follow-up for diabetes management",
            soap_note={
                "subjective": {
                    "complaint": "Feeling better, reduced fatigue",
                    "compliance": "Taking Metformin regularly"
                },
                "objective": {
                    "vitals": {
                        "bp": "135/85",
                        "pulse": 76,
                        "weight": 74
                    },
                    "labs": {
                        "hba1c": "7.8%",
                        "fasting_glucose": "142 mg/dL"
                    }
                },
                "assessment": {
                    "diagnosis": "Type 2 DM - Under control",
                    "notes": "HbA1c trending down"
                },
                "plan": {
                    "medications": ["Increase Metformin to 1000mg BD"],
                    "lifestyle": "Continue diet and exercise",
                    "followup": "1 month"
                }
            }
        )
        db.add(encounter2)
        
        encounter3 = Encounter(
            patient_id=patient2.id,
            doctor_id=doctor.id,
            clinic_id=clinic.id,
            encounter_type="opd",
            status="completed",
            start_time=datetime.utcnow() - timedelta(days=3),
            end_time=datetime.utcnow() - timedelta(days=3, hours=-1),
            chief_complaint="Hypertension screening",
            soap_note={
                "subjective": {
                    "complaint": "Routine checkup, family history of HTN"
                },
                "objective": {
                    "vitals": {
                        "bp": "145/92",
                        "pulse": 82,
                        "weight": 68
                    }
                },
                "assessment": {
                    "diagnosis": "Stage 1 Hypertension",
                    "icd_code": "I10"
                },
                "plan": {
                    "medications": ["Amlodipine 5mg OD"],
                    "lifestyle": "Low salt diet, regular exercise",
                    "followup": "2 weeks"
                }
            }
        )
        db.add(encounter3)
        db.flush()
        
        # 5. Create Prescriptions
        prescription1 = Prescription(
            prescription_number=f"RX-{datetime.now().strftime('%Y%m%d')}-00001",
            encounter_id=encounter2.id,
            patient_id=patient1.id,
            doctor_id=doctor.id,
            status="signed",
            medications=[
                {
                    "generic_name": "METFORMIN",
                    "brand_suggestions": ["Glycomet", "Metsmall"],
                    "strength": "1000mg",
                    "dosage_form": "tablet",
                    "route": "oral",
                    "frequency": "Twice daily",
                    "duration_days": 30,
                    "quantity": 60,
                    "instructions": "Take after meals"
                }
            ],
            instructions="Monitor blood glucose levels. Follow up in 1 month.",
            signature_hash="abc123def456",
            signature_timestamp=datetime.utcnow(),
            qr_code_data=f"https://integmed.health/rx/RX-{datetime.now().strftime('%Y%m%d')}-00001",
            nmc_compliant=True,
            generic_first=True
        )
        db.add(prescription1)
        
        # 6. Create FHIR Observations (Lab Results)
        observation1 = FHIRResource(
            resource_type="Observation",
            resource_id="obs-hba1c-001",
            patient_id=patient1.id,
            encounter_id=encounter2.id,
            category="laboratory",
            code="4548-4",  # LOINC code for HbA1c
            effective_date=(datetime.utcnow() - timedelta(days=2)).date(),
            value_numeric=7.8,
            value_text="7.8%",
            resource={
                "resourceType": "Observation",
                "id": "obs-hba1c-001",
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "4548-4",
                        "display": "Hemoglobin A1c/Hemoglobin.total in Blood"
                    }],
                    "text": "HbA1c"
                },
                "valueQuantity": {
                    "value": 7.8,
                    "unit": "%",
                    "system": "http://unitsofmeasure.org",
                    "code": "%"
                }
            },
            source="manual",
            source_system="Apollo Diagnostics Mumbai"
        )
        db.add(observation1)
        
        # Commit all changes
        db.commit()
        
        logger.info("✅ Database seeded successfully!")
        logger.info(f"   📊 Created: 1 clinic, 1 doctor, 2 patients, 3 encounters, 1 prescription, 1 lab result")
        logger.info(f"   🔑 Demo doctor: {doctor.mobile}")
        logger.info(f"   🔑 Demo patients: {patient1.mobile}, {patient2.mobile}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
