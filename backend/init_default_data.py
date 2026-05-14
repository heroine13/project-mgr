"""
Initialize default data: roles, departments, super admin user
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user_mgmt import Role, Department
from app.models.i18n import Language
from app.auth import hash_password

def init_default_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Role).count() > 0:
            print("Default data already exists, skipping...")
            return

        print("Initializing default data...")

        # Create roles
        roles = [
            Role(name="super_admin", description="Super Administrator", permissions='*'),
            Role(name="admin", description="Administrator", permissions='admin'),
            Role(name="manager", description="Project Manager", permissions='manager'),
            Role(name="member", description="Team Member", permissions='member'),
            Role(name="viewer", description="Viewer", permissions='viewer'),
        ]
        for role in roles:
            db.add(role)
        db.commit()
        print(f"Created {len(roles)} roles")

        # Create default department
        dept = Department(name="Development", code="DEV", description="Development Department")
        db.add(dept)
        db.commit()
        print("Created default department")

        # Create super admin user
        existing = db.query(Role).filter_by(name="super_admin").first()
        admin = db.query(db.__class__).first() if False else None
        from app.models.user import User
        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@goldfon.cn",
                hashed_password=hash_password("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True,
                role_id=existing.id if existing else 1
            )
            db.add(admin)
            db.commit()
            print("Created super admin user (username: admin, password: admin123)")
        else:
            print("Admin user already exists")

        # Create default languages
        if db.query(Language).count() == 0:
            langs = [
                Language(code="zh-CN", name="简体中文", native_name="简体中文", is_default=True, is_active=True, display_order=1),
                Language(code="en", name="English", native_name="English", is_default=False, is_active=True, display_order=2),
            ]
            for lang in langs:
                db.add(lang)
            db.commit()
            print(f"Created {len(langs)} default languages")

        print("Default data initialization complete!")
    finally:
        db.close()

if __name__ == "__main__":
    init_default_data()
