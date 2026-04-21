"""
Performance Optimization - Caching and Pagination Utilities
"""

from functools import wraps
from typing import Optional, Callable
import time
import hashlib
import json


class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}  # Time to live
    
    def get(self, key: str) -> Optional[any]:
        if key in self._cache:
            if key in self._ttl and time.time() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: any, ttl: int = 300):
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl
    
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    def clear(self):
        self._cache.clear()
        self._ttl.clear()


# Global cache instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            result = cache_manager.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_manager.set(key, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str = None):
    """Invalidate cache by pattern"""
    if pattern is None:
        cache_manager.clear()
    else:
        keys_to_delete = [k for k in cache_manager._cache.keys() if pattern in k]
        for key in keys_to_delete:
            cache_manager.delete(key)


class OptimizedPaginator:
    """Optimized pagination helper"""
    
    @staticmethod
    def paginate(query, page: int = 1, page_size: int = 20, max_page_size: int = 100):
        """Apply pagination with limits"""
        page = max(1, page)
        page_size = min(max(1, page_size), max_page_size)
        skip = (page - 1) * page_size
        
        total = query.count()
        items = query.offset(skip).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }


# Query optimization helpers
def add_indexes_if_not_exists(db, table_name: str, columns: list):
    """Add database indexes for better query performance"""
    # This would typically be handled by migrations
    pass