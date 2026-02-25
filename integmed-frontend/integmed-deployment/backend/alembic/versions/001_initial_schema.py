"""Initial schema - users, patients, encounters, prescriptions

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-02-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table (Doctors, Nurses, Admin)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('hpr_id', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('mobile', sa.String(15), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('system', sa.String(20), nullable=False),  # 'allopathy', 'ayurveda', 'homeopathy', 'unani'
        sa.Column('qualification', sa.String(255), nullable=True),
        sa.Column('registration_number', sa.String(100), unique=True, nullable=True),
        sa.Column('registration_council', sa.String(255), nullable=True),
        sa.Column('specialization', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=False),  # 'doctor', 'nurse', 'admin'
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create index on system and role for filtering
    op.create_index('idx_users_system_role', 'users', ['system', 'role'])

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('abha_number', sa.String(17), unique=True, nullable=True, index=True),
        sa.Column('abha_address', sa.String(255), unique=True, nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('mobile', sa.String(15), nullable=True, index=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('year_of_birth', sa.Integer(), nullable=True),
        sa.Column('address', postgresql.JSONB(), nullable=True),
        sa.Column('emergency_contact', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create clinics table
    op.create_table(
        'clinics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('hip_id', sa.String(100), unique=True, nullable=True),  # ABDM HIP ID
        sa.Column('address', postgresql.JSONB(), nullable=True),
        sa.Column('phone', sa.String(15), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create encounters table
    op.create_table(
        'encounters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clinics.id'), nullable=True),
        sa.Column('encounter_type', sa.String(50), nullable=False),  # 'opd', 'emergency', 'followup'
        sa.Column('status', sa.String(50), nullable=False),  # 'scheduled', 'in_progress', 'completed'
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('soap_note', postgresql.JSONB(), nullable=True),  # Full SOAP structure
        sa.Column('ayush_assessment', postgresql.JSONB(), nullable=True),  # Prakriti, Vikriti, Nadi
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create composite index for patient timeline queries
    op.create_index('idx_encounters_patient_time', 'encounters', ['patient_id', 'start_time'])

    # Create prescriptions table
    op.create_table(
        'prescriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('prescription_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('encounter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('encounters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False),  # 'draft', 'signed', 'dispensed', 'cancelled'
        sa.Column('medications', postgresql.JSONB(), nullable=False),  # Array of medication objects
        sa.Column('ayush_medications', postgresql.JSONB(), nullable=True),  # Array of AYUSH medications
        sa.Column('instructions', sa.Text(), nullable=True),
        
        # Digital Signature
        sa.Column('signature_hash', sa.String(255), nullable=True),
        sa.Column('signature_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('signature_certificate', sa.Text(), nullable=True),
        
        # QR Code
        sa.Column('qr_code_data', sa.Text(), nullable=True),
        sa.Column('qr_code_image', sa.Text(), nullable=True),  # Base64 encoded
        
        # ABDM Integration
        sa.Column('abdm_pushed', sa.Boolean(), default=False),
        sa.Column('abdm_push_timestamp', sa.DateTime(timezone=True), nullable=True),
        
        # Compliance
        sa.Column('nmc_compliant', sa.Boolean(), default=True),
        sa.Column('generic_first', sa.Boolean(), default=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Index for status queries
    op.create_index('idx_prescriptions_status', 'prescriptions', ['status'])


def downgrade() -> None:
    op.drop_table('prescriptions')
    op.drop_table('encounters')
    op.drop_table('clinics')
    op.drop_table('patients')
    op.drop_table('users')
