"""Wearable data with TimescaleDB

Revision ID: 003_wearable_data
Revises: 002_fhir_abdm
Create Date: 2026-02-09 10:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_wearable_data'
down_revision = '002_fhir_abdm'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable TimescaleDB extension (requires superuser or pre-enabled)
    # op.execute('CREATE EXTENSION IF NOT EXISTS timescaledb')
    
    # Create wearable data table
    op.create_table(
        'wearable_data',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_type', sa.String(50), nullable=False),  # 'fitbit', 'apple_watch', 'garmin'
        sa.Column('metric_type', sa.String(50), nullable=False, index=True),  # 'heart_rate', 'hrv', 'sleep', 'steps'
        sa.Column('value', sa.Numeric(), nullable=True),
        sa.Column('unit', sa.String(20), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),  # Additional device-specific data
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Convert to hypertable (TimescaleDB)
    # This creates time-series partitions for efficient time-based queries
    op.execute(
        "SELECT create_hypertable('wearable_data', 'time', if_not_exists => TRUE)"
    )
    
    # Create composite index for patient queries
    op.create_index('idx_wearable_patient_time', 'wearable_data', ['patient_id', 'time'], postgresql_using='btree')
    op.create_index('idx_wearable_metric_type', 'wearable_data', ['metric_type'])
    
    # Create continuous aggregate for daily averages (TimescaleDB feature)
    op.execute("""
        CREATE MATERIALIZED VIEW wearable_daily_avg
        WITH (timescaledb.continuous) AS
        SELECT 
            patient_id,
            device_type,
            metric_type,
            time_bucket('1 day', time) AS day,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            COUNT(*) as data_points
        FROM wearable_data
        GROUP BY patient_id, device_type, metric_type, day
        WITH NO DATA;
    """)
    
    # Add refresh policy to update the materialized view automatically
    op.execute("""
        SELECT add_continuous_aggregate_policy('wearable_daily_avg',
            start_offset => INTERVAL '3 days',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '1 hour');
    """)


def downgrade() -> None:
    # Remove continuous aggregate
    op.execute("DROP MATERIALIZED VIEW IF EXISTS wearable_daily_avg")
    
    # Drop table (this also removes the hypertable)
    op.drop_table('wearable_data')
