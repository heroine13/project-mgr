"""
pytest 配置文件
提供测试夹具和配置
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app


# 测试数据库引擎 (SQLite 内存数据库)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    # 覆盖数据库依赖
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 清除依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """创建示例用户"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_project(db_session, sample_user):
    """创建示例项目"""
    from app.models.project import Project
    
    project = Project(
        name="Test Project",
        description="A test project",
        owner_id=sample_user.id,
        status="active",
        progress=0
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_task(db_session, sample_project, sample_user):
    """创建示例任务"""
    from app.models.task import Task
    
    task = Task(
        title="Test Task",
        description="A test task",
        project_id=sample_project.id,
        assignee_id=sample_user.id,
        status="todo",
        priority="medium",
        progress=0
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def auth_token(client, sample_user):
    """获取认证令牌"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """获取认证请求头"""
    return {"Authorization": f"Bearer {auth_token}"}