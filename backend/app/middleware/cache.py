"""
API Response Caching Middleware
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import hashlib

from app.core.performance import cache_manager, invalidate_cache


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching API responses"""
    
    # Routes that should not be cached
    NO_CACHE_ROUTES = [
        "/auth/login",
        "/auth/register",
        "/users/",
        "/notifications/unread"
    ]
    
    # Cache TTL in seconds
    CACHE_TTL = 300  # 5 minutes
    
    async def dispatch(self, request: Request, call_next):
        # Skip non-GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Check if route should be cached
        path = request.url.path
        if any(no_cache in path for no_cache in self.NO_CACHE_ROUTES):
            return await call_next(request)
        
        # Generate cache key
        cache_key = f"api:{path}:{hashlib.md5(str(request.query_params).encode()).hexdigest()}"
        
        # Check cache
        cached_response = cache_manager.get(cache_key)
        if cached_response:
            return JSONResponse(content=cached_response)
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            try:
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Parse and cache
                import json
                data = json.loads(body)
                cache_manager.set(cache_key, data, self.CACHE_TTL)
                
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            except:
                pass
        
        return response


def clear_api_cache():
    """Clear all API cache"""
    invalidate_cache("api:")