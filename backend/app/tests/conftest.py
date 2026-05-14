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

# 导入所有模型，确保它们被注册到 Base.metadata
from app.models import User, Task, Project, Notification, NotificationPreference, EmailQueue, Comment, GanttTask


# 测试数据库引擎 (SQLite 内存数据库)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 全局变量存储当前测试会话
_test_db_session = None


def override_get_db():
    """覆盖数据库依赖 - 返回测试会话"""
    global _test_db_session
    if _test_db_session is not None:
        try:
            yield _test_db_session
        finally:
            pass
    else:
        # 如果没有测试会话，创建新的
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """自动设置测试数据库"""
    global _test_db_session
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    _test_db_session = TestingSessionLocal()
    
    yield
    
    # 清理
    _test_db_session.close()
    _test_db_session = None
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """创建测试客户端 - 必须在 setup_test_db 之后"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    """提供测试数据库会话"""
    return _test_db_session


@pytest.fixture
def sample_user(db_session):
    """创建示例用户"""
    import bcrypt
    
    hashed_password = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode()
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
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
    project = Project(
        name="Test Project",
        description="A test project",
        owner_id=sample_user.id,
        status="active"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_task(db_session, sample_project, sample_user):
    """创建示例任务"""
    from app.models.task import TaskStatus, TaskPriority
    
    task = Task(
        title="Test Task",
        description="A test task",
        project_id=sample_project.id,
        assignee_id=sample_user.id,
        status=TaskStatus.PENDING.value,
        priority=TaskPriority.MEDIUM.value,
        created_by=sample_user.id
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