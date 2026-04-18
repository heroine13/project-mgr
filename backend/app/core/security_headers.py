"""
安全中间件
提供额外的安全防护
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import hashlib


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单速率限制中间件"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查速率限制
        current_time = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # 清理过期的请求记录
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"}
            )
        
        # 记录请求
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加自定义头
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录日志
        print(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        return response


class SecurityHeaders:
    """安全头配置类"""
    
    @staticmethod
    def get_csp() -> str:
        """获取 Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https: wss:; "
            "frame-ancestors 'none';"
        )
    
    @staticmethod
    def get_hsts() -> str:
        """获取 HSTS 配置"""
        return "max-age=31536000; includeSubDomains; preload"
    
    @staticmethod
    def get_referrer_policy() -> str:
        """获取 Referrer Policy"""
        return "strict-origin-when-cross-origin"


def generate_csrf_token() -> str:
    """生成 CSRF 令牌"""
    import secrets
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """验证 CSRF 令牌"""
    import hmac
    return hmac.compare_digest(token, stored_token)


def hash_sensitive_data(data: str) -> str:
    """对敏感数据进行处理"""
    return hashlib.sha256(data.encode()).hexdigest()


def sanitize_input(user_input: str) -> str:
    """清理用户输入，防止 XSS"""
    import html
    return html.escape(user_input)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    Returns:
        (是否通过, 错误信息)
    """
    if len(password) < 8:
        return False, "密码长度至少为 8 个字符"
    
    if not any(c.isupper() for c in password):
        return False, "密码必须包含至少一个大写字母"
    
    if not any(c.islower() for c in password):
        return False, "密码必须包含至少一个小写字母"
    
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含至少一个数字"
    
    return True, ""


def generate_secure_token(length: int = 32) -> str:
    """生成安全随机令牌"""
    import secrets
    return secrets.token_urlsafe(length)