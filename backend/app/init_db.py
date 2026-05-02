"""
数据库初始化脚本 - 创建表并添加测试数据
"""
import sys
sys.path.insert(0, '/app')

from app.core.database import engine, Base, SessionLocal
# 导入所有模型以确保关系正确配置
from app.models.user import User
from app.models.user_mgmt import Role, Department, UserProfile, AuditLog
from app.models import *  # 导入所有模型
from app.auth import hash_password

def init_database():
    """初始化数据库表和测试数据"""
    
    # 创建所有表
    print("📦 正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    db = SessionLocal()
    
    try:
        # 检查是否已有角色
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            print("📋 正在创建角色...")
            roles = [
                Role(name="admin", description="系统管理员", permissions='{"all": true}', is_system=True),
                Role(name="pm", description="项目经理", permissions='{"projects": true, "tasks": true}', is_system=True),
                Role(name="member", description="团队成员", permissions='{"tasks": true}', is_system=True),
            ]
            db.add_all(roles)
            db.commit()
            print("✅ 角色创建完成")
        
        # 检查是否已有用户
        existing_users = db.query(User).count()
        if existing_users == 0:
            print("👤 正在创建测试用户...")
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            pm_role = db.query(Role).filter(Role.name == "pm").first()
            member_role = db.query(Role).filter(Role.name == "member").first()
            
            users = [
                User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=hash_password("admin123"),
                    full_name="系统管理员",
                    is_active=True,
                    is_superuser=True,
                    role_id=admin_role.id if admin_role else None
                ),
                User(
                    username="user",
                    email="user@example.com",
                    hashed_password=hash_password("user123"),
                    full_name="普通用户",
                    is_active=True,
                    role_id=member_role.id if member_role else None
                ),
                User(
                    username="pm",
                    email="pm@example.com",
                    hashed_password=hash_password("pm123"),
                    full_name="项目经理",
                    is_active=True,
                    role_id=pm_role.id if pm_role else None
                ),
                User(
                    username="member",
                    email="member@example.com",
                    hashed_password=hash_password("member123"),
                    full_name="团队成员",
                    is_active=True,
                    role_id=member_role.id if member_role else None
                ),
            ]
            db.add_all(users)
            db.commit()
            print("✅ 测试用户创建完成")
        
        # 检查是否已有部门
        existing_depts = db.query(Department).count()
        if existing_depts == 0:
            print("🏢 正在创建部门...")
            departments = [
                Department(name="研发部", code="RD", description="研发部门"),
                Department(name="产品部", code="PD", description="产品部门"),
                Department(name="测试部", code="QA", description="测试部门"),
                Department(name="运维部", code="OPS", description="运维部门"),
            ]
            db.add_all(departments)
            db.commit()
            print("✅ 部门创建完成")
        
        print("\n🎉 数据库初始化完成！")
        print("\n📝 测试账号：")
        print("  - admin / admin123 (管理员)")
        print("  - user / user123 (普通用户)")
        print("  - pm / pm123 (项目经理)")
        print("  - member / member123 (团队成员)")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()