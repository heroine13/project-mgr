#!/usr/bin/env python
"""
初始化测试数据库 - 创建基础数据
"""
import os
os.chdir('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash

# 创建数据库引擎
engine = create_engine('sqlite:////tmp/test_db/project_mgr.db', connect_args={'check_same_thread': False})

# 导入所有模型以确保关系正确初始化
from app.models.user import User
from app.models.user_mgmt import Role, Department

# 导入所有其他模型
from app.models import (
    notification, issue, task, project, document,
    resource, comment, calendar, backup
)

# 创建所有表
from app.core.database import Base
Base.metadata.create_all(bind=engine)
print('数据库表创建完成')

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 检查是否已有数据
    existing_users = db.query(User).count()
    if existing_users > 0:
        print(f'数据库已有 {existing_users} 个用户:')
        users = db.query(User).all()
        for u in users:
            print(f'  - {u.username} (email: {u.email})')
    else:
        # 创建角色
        admin_role = Role(name='管理员', description='系统管理员', is_system=True)
        user_role = Role(name='普通用户', description='普通用户角色', is_system=False)
        db.add(admin_role)
        db.add(user_role)
        db.commit()
        db.refresh(admin_role)
        db.refresh(user_role)
        print(f'角色创建完成: 管理员(ID:{admin_role.id}), 普通用户(ID:{user_role.id})')
        
        # 创建测试用户
        admin_user = User(
            username='admin',
            email='admin@test.com',
            full_name='系统管理员',
            hashed_password=get_password_hash('admin123'),
            role_id=admin_role.id,
            is_active=True,
            is_superuser=True
        )
        
        test_user = User(
            username='testuser',
            email='test@test.com',
            full_name='测试用户',
            hashed_password=get_password_hash('123456'),
            role_id=user_role.id,
            is_active=True
        )
        
        db.add(admin_user)
        db.add(test_user)
        db.commit()
        print(f'用户创建完成: admin, testuser')
        
        # 创建测试部门
        depts = [
            Department(name='技术部', code='TECH', parent_id=None),
            Department(name='产品部', code='PRODUCT', parent_id=None),
            Department(name='设计部', code='DESIGN', parent_id=None),
        ]
        for d in depts:
            db.add(d)
        db.commit()
        print(f'部门创建完成')
    
    print('\n初始化完成！')
    print('测试账号:')
    print('  - admin / admin123 (管理员)')
    print('  - testuser / 123456 (普通用户)')
    
except Exception as e:
    print(f'操作失败: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()