#!/bin/bash
set -e

echo "🏥 IntegMed Backend - Starting..."

# Wait for database
echo "⏳ Waiting for database..."
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

until nc -z $DB_HOST $DB_PORT 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "✅ Database is ready!"

# Run migrations
echo "🔄 Running Alembic migrations..."
alembic upgrade head

# Seed data (only in development)
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🌱 Seeding demo data..."
    python scripts/seed_data.py || echo "⚠️ Seed data already exists or failed"
fi

echo "🚀 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4}
