from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 根据配置选择数据库URL
def get_database_url():
    db_type = settings.DATABASE_TYPE.lower()
    
    if db_type == "mysql":
        if not all([settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_PASSWORD, settings.MYSQL_DATABASE]):
            raise ValueError("MySQL配置不完整")
        return f"mysql+mysqlconnector://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    
    elif db_type == "sqlserver":
        if not all([settings.SQLSERVER_HOST, settings.SQLSERVER_USER, settings.SQLSERVER_PASSWORD, settings.SQLSERVER_DATABASE]):
            raise ValueError("SQL Server配置不完整")
        return f"mssql+pymssql://{settings.SQLSERVER_USER}:{settings.SQLSERVER_PASSWORD}@{settings.SQLSERVER_HOST}:{settings.SQLSERVER_PORT}/{settings.SQLSERVER_DATABASE}"
    
    elif db_type == "sqlite":
        return settings.DATABASE_URL
    
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")

# 创建数据库引擎
try:
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if settings.DATABASE_TYPE == "sqlite" else {},
        echo=settings.ENVIRONMENT == "development"
    )
    logger.info(f"数据库连接成功: {settings.DATABASE_TYPE}")
except Exception as e:
    logger.error(f"数据库连接失败: {e}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()