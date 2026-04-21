"""
Security Configuration
"""

import os
from typing import List, Optional


class SecurityConfig:
    """Security configuration settings"""
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.environ.get("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Password Policy
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False
    PASSWORD_MAX_AGE_DAYS = 90
    
    # Account Security
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
    SESSION_TIMEOUT_MINUTES = 30
    
    # API Security
    API_KEY_HEADER = "X-API-Key"
    API_RATE_LIMIT_PER_MINUTE = 100
    
    # File Upload Security
    ALLOWED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"]
    MAX_FILE_SIZE_MB = 10
    UPLOAD_DIR = "./uploads"
    
    # Logging Security Events
    LOG_SECURITY_EVENTS = True
    SECURITY_LOG_FILE = "./logs/security.log"
    
    # Trusted Proxies
    TRUSTED_PROXIES = os.environ.get("TRUSTED_PROXIES", "127.0.0.1").split(",")


# Role-based Access Control
class RBAC:
    """Role-based Access Control definitions"""
    
    ROLES = {
        "admin": [
            "users:read", "users:write", "users:delete",
            "projects:read", "projects:write", "projects:delete",
            "tasks:read", "tasks:write", "tasks:delete",
            "issues:read", "issues:write", "issues:delete",
            "reports:read", "reports:export",
            "settings:read", "settings:write",
            "audit:read", "backup:manage",
            "workflows:manage", "templates:manage"
        ],
        "manager": [
            "projects:read", "projects:write",
            "tasks:read", "tasks:write", "tasks:delete",
            "issues:read", "issues:write",
            "reports:read", "reports:export",
            "team:manage"
        ],
        "member": [
            "projects:read",
            "tasks:read", "tasks:write",
            "issues:read", "issues:write",
            "reports:read"
        ],
        "client": [
            "projects:read",
            "issues:read"
        ]
    }
    
    @classmethod
    def get_permissions(cls, role: str) -> List[str]:
        """Get permissions for a role"""
        return cls.ROLES.get(role, [])
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Check if role has permission"""
        return permission in cls.get_permissions(role)


# Permission Checker
def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if user has required permission"""
    return RBAC.has_permission(user_role, required_permission)


# Security utilities
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    # Basic sanitization
    dangerous_chars = [
        ("<", "&lt;"),
        (">", "&gt;"),
        ("\"", "&quot;"),
        ("'", "&#x27;"),
        ("/", "&#x2F;")
    ]
    
    for char, replacement in dangerous_chars:
        text = text.replace(char, replacement)
    
    return text


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    config = SecurityConfig()
    
    if len(password) < config.PASSWORD_MIN_LENGTH:
        return False, f"密码长度至少{config.PASSWORD_MIN_LENGTH}位"
    
    if config.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "密码必须包含大写字母"
    
    if config.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "密码必须包含小写字母"
    
    if config.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    
    return True, ""


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import hashlib
    # In production, use bcrypt: import bcrypt; return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    import hashlib
    # In production, use bcrypt: import bcrypt; return bcrypt.checkpw(password.encode(), hashed.encode())
    return hashlib.sha256(password.encode()).hexdigest() == hashed