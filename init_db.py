#!/usr/bin/env python3
"""初始化SQLite数据库"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
from app.models.user import User
from app.models.user_mgmt import Role, Department
from app.core.database import Base

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'project_mgr.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
print(f'数据库: {db_path}')

Session = sessionmaker(bind=engine)
db = Session()

try:
    if db.query(User).count() > 0:
        print('已有数据')
    else:
        admin_role = Role(name='管理员', description='系统管理员', is_system=True)
        user_role = Role(name='普通用户', description='普通用户', is_system=False)
        db.add_all([admin_role, user_role])
        db.commit()
        
        admin = User(username='admin', email='admin@test.com', full_name='管理员', 
                     hashed_password=get_password_hash('admin123'), role_id=1, is_active=True, is_superuser=True)
        test = User(username='testuser', email='test@test.com', full_name='测试用户',
                    hashed_password=get_password_hash('123456'), role_id=2, is_active=True)
        db.add_all([admin, test])
        
        depts = [Department(name='技术部', code='TECH'), 
                 Department(name='产品部', code='PRODUCT'),
                 Department(name='设计部', code='DESIGN')]
        db.add_all(depts)
        db.commit()
        print('数据初始化完成!')
        print('账号: admin/admin123, testuser/123456')
except Exception as e:
    print(f'错误: {e}')
    db.rollback()
finally:
    db.close()