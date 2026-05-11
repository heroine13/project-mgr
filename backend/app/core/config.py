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
    
    # CORS配置（逗号分隔字符串，环境变量可覆盖）
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 前端代理地址（开发环境）
    VITE_API_BASE_URL: str = "http://localhost:8000"
    # WebSocket 地址（开发环境）
    VITE_WS_URL: str = "ws://localhost:8000"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()