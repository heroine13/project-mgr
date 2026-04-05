#!/bin/bash

# Database initialization script

set -e

echo "Initializing Project Management System database..."

# Check if database is ready
echo "Waiting for MySQL database to be ready..."
until mysql -h localhost -u root -prootpassword -e "SELECT 1" > /dev/null 2>&1; do
    echo -n "."
    sleep 1
done
echo "MySQL is ready!"

# Initialize database schema using Alembic
echo "Creating database tables..."
cd backend

# Create tables using Alembic
if [ -f alembic.ini ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
else
    echo "Alembic not configured, creating tables from models..."
    python -c "
from app.db.database import Base, engine
from app.models import user, task, project
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
fi

# Create initial admin user
echo "Creating initial admin user..."
python -c "
from app.db.database import SessionLocal
from app.crud.user import create_user
from app.schemas.auth import UserCreate

db = SessionLocal()
try:
    admin_data = UserCreate(
        username='admin',
        email='admin@projectmgr.local',
        password='Admin123!',
        full_name='Administrator'
    )
    user = create_user(db, admin_data)
    print(f'Admin user created: {user.username}')
except Exception as e:
    print(f'Admin user may already exist: {e}')
finally:
    db.close()
"

echo "Database initialization completed!"