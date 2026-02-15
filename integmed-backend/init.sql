-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE integmed TO integmed;
