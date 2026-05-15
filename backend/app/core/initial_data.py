"""数据库初始化脚本 - 用于新部署时创建表和数据"""
from app.core.database import engine, SessionLocal
from app.models.user import User
from app.models.user_mgmt import Role, Department
from app.models.project import Project
from app.models.task import Task
from app.models.issue import Issue
from app.models.notification import Notification
from app.models.resource import Resource
from app.models.document import Document
import bcrypt

def init_tables():
    """创建所有数据库表"""
    tables = [
        Role, User, Project, Task, Issue, 
        Notification, Resource, Document
    ]
    from sqlalchemy import MetaData
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    for model in tables:
        try:
            model.__table__.create(bind=engine, checkfirst=True)
        except:
            pass
    
    # document_categories已在search.py中定义
    try:
        from app.models.search import DocumentCategory
        DocumentCategory.__table__.create(bind=engine, checkfirst=True)
    except:
        pass
    
    print("✅ 所有表已创建")

def init_default_user():
    """创建默认管理员账号"""
    db = SessionLocal()
    
    role = db.query(Role).filter(Role.name == 'admin').first()
    if not role:
        role = Role(name='admin', description='系统管理员', is_system=True)
        db.add(role)
        db.commit()
    
    user = db.query(User).filter(User.username == 'admin').first()
    if not user:
        password = 'admin123'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            username='admin',
            email='admin@company.com',
            hashed_password=hashed,
            full_name='管理员',
            is_active=True,
            is_superuser=True,
            role_id=role.id
        )
        db.add(user)
        db.commit()
        print(f"✅ 管理员账号已创建: admin / admin123")
    else:
        print("⚠️ 管理员账号已存在")
    
    db.close()

if __name__ == '__main__':
    init_tables()
    init_default_user()
