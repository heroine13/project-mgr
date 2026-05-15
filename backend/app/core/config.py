from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "Project Management System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置 - 支持环境变量配置，多个域名用逗号分隔
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://frontend:3000",
    ]
    
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./project_mgr.db"
    DATABASE_TYPE: str = "sqlite"  # sqlite, mysql, sqlserver
    
    # MySQL配置
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: Optional[int] = 3306
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DATABASE: Optional[str] = None
    
    # SQL Server配置
    SQLSERVER_HOST: Optional[str] = None
    SQLSERVER_PORT: Optional[int] = 1433
    SQLSERVER_USER: Optional[str] = None
    SQLSERVER_PASSWORD: Optional[str] = None
    SQLSERVER_DATABASE: Optional[str] = None
    
    # Redis配置
    REDIS_HOST: Optional[str] = "localhost"
    REDIS_PORT: Optional[int] = 6379
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 从环境变量读取 CORS_ORIGINS 并合并
        cors_env = os.environ.get("CORS_ORIGINS", "")
        if cors_env:
            extra_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
            self.BACKEND_CORS_ORIGINS = list(set(self.BACKEND_CORS_ORIGINS + extra_origins))
        
        # 如果DATABASE_URL是mysql，自动设置类型和MySQL配置
        if self.DATABASE_URL and 'mysql' in self.DATABASE_URL.lower():
            self.DATABASE_TYPE = 'mysql'
            import urllib.parse
            parsed = urllib.parse.urlparse(self.DATABASE_URL.replace('mysql+mysqlconnector://', 'mysql://'))
            self.MYSQL_HOST = parsed.hostname or 'localhost'
            self.MYSQL_PORT = parsed.port or 3306
            self.MYSQL_USER = parsed.username
            self.MYSQL_PASSWORD = parsed.password
            self.MYSQL_DATABASE = parsed.path.lstrip('/') if parsed.path else None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
