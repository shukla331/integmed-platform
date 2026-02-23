"""FHIR resources and ABDM integration tables

Revision ID: 002_fhir_abdm
Revises: 001_initial_schema
Create Date: 2026-02-09 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_fhir_abdm'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create FHIR resources table (flexible storage for all FHIR types)
    op.create_table(
        'fhir_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('resource_type', sa.String(50), nullable=False, index=True),  # 'Observation', 'Condition', etc.
        sa.Column('resource_id', sa.String(255), nullable=False),  # FHIR resource ID
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('encounter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('encounters.id', ondelete='CASCADE'), nullable=True),
        
        # Full FHIR resource as JSONB
        sa.Column('resource', postgresql.JSONB(), nullable=False),
        
        # Extracted fields for efficient querying
        sa.Column('category', sa.String(100), nullable=True, index=True),  # 'vital-signs', 'laboratory', 'imaging'
        sa.Column('code', sa.String(100), nullable=True, index=True),  # LOINC/SNOMED code
        sa.Column('effective_date', sa.Date(), nullable=True, index=True),
        sa.Column('value_numeric', sa.Numeric(), nullable=True),
        sa.Column('value_text', sa.Text(), nullable=True),
        
        # Source tracking
        sa.Column('source', sa.String(100), nullable=True),  # 'abdm', 'manual', 'wearable', 'lab_integration'
        sa.Column('source_system', sa.String(255), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create GIN index for JSONB queries
    op.execute('CREATE INDEX idx_fhir_resource_gin ON fhir_resources USING gin(resource)')
    
    # Create composite index for patient queries
    op.create_index('idx_fhir_patient_category_date', 'fhir_resources', ['patient_id', 'category', 'effective_date'])

    # Create ABDM consent requests table
    op.create_table(
        'abdm_consents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('consent_request_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('purpose', sa.String(100), nullable=False),  # 'CAREMGT', 'BTG', 'PUBHLTH', etc.
        sa.Column('hi_types', postgresql.JSONB(), nullable=False),  # Array of health info types
        sa.Column('date_range', postgresql.JSONB(), nullable=False),  # {from, to} dates
        sa.Column('status', sa.String(50), nullable=False, index=True),  # 'requested', 'granted', 'denied', 'expired'
        sa.Column('consent_artifact', postgresql.JSONB(), nullable=True),  # Full consent artifact from ABDM
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create ABDM data requests table
    op.create_table(
        'abdm_data_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('transaction_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('consent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('abdm_consents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, index=True),  # 'requested', 'processing', 'completed', 'failed'
        sa.Column('hip_ids', postgresql.JSONB(), nullable=True),  # Array of HIP IDs
        sa.Column('data_push_url', sa.Text(), nullable=True),
        sa.Column('encryption_key', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(100), nullable=False, index=True),  # 'view_patient', 'create_prescription', etc.
        sa.Column('resource_type', sa.String(50), nullable=True),  # 'patient', 'prescription', 'fhir_resource'
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_data', postgresql.JSONB(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )
    
    # Create index for action queries
    op.create_index('idx_audit_action_time', 'audit_logs', ['action', 'created_at'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('abdm_data_requests')
    op.drop_table('abdm_consents')
    op.drop_table('fhir_resources')
