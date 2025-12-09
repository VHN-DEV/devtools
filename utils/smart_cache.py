#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module smart_cache - Hệ thống cache thông minh

Mục đích: Cải thiện performance với caching thông minh, TTL, invalidation
Lý do: Giảm thời gian load và tăng tốc độ xử lý
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta
from functools import wraps


class SmartCache:
    """
    Class quản lý cache thông minh với TTL và invalidation
    
    Mục đích: Cache dữ liệu với thời gian sống và tự động invalidate
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 3600):
        """
        Khởi tạo SmartCache
        
        Args:
            cache_dir: Thư mục cache (mặc định: plugins/cache)
            default_ttl: Thời gian sống mặc định (giây)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "plugins" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.max_memory_items = 100  # Giới hạn số items trong memory cache
    
    def _get_cache_key(self, key: str) -> str:
        """Tạo cache key từ string"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Lấy đường dẫn file cache"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Lấy giá trị từ cache
        
        Args:
            key: Cache key
            default: Giá trị mặc định nếu không tìm thấy
        
        Returns:
            Giá trị cached hoặc default
        """
        # Kiểm tra memory cache trước
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if self._is_valid(item):
                return item['value']
            else:
                # Expired, xóa khỏi memory
                del self.memory_cache[key]
        
        # Kiểm tra file cache
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                
                if self._is_valid(item):
                    # Lưu vào memory cache
                    self._add_to_memory(key, item)
                    return item['value']
                else:
                    # Expired, xóa file
                    cache_file.unlink()
            except Exception:
                pass
        
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Lưu giá trị vào cache
        
        Args:
            key: Cache key
            value: Giá trị cần cache
            ttl: Thời gian sống (None = dùng default_ttl)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = time.time() + ttl
        
        item = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        
        # Lưu vào memory cache
        self._add_to_memory(key, item)
        
        # Lưu vào file cache
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(item, f, ensure_ascii=False)
        except Exception:
            pass
    
    def _add_to_memory(self, key: str, item: Dict[str, Any]):
        """Thêm vào memory cache (với giới hạn)"""
        # Nếu đã đầy, xóa item cũ nhất
        if len(self.memory_cache) >= self.max_memory_items:
            # Xóa item cũ nhất (FIFO)
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = item
    
    def _is_valid(self, item: Dict[str, Any]) -> bool:
        """Kiểm tra cache item còn hiệu lực không"""
        expires_at = item.get('expires_at', 0)
        return time.time() < expires_at
    
    def invalidate(self, key: str):
        """
        Xóa cache cho key cụ thể
        
        Args:
            key: Cache key cần xóa
        """
        # Xóa khỏi memory
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Xóa file
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()
    
    def clear(self):
        """Xóa tất cả cache"""
        # Xóa memory cache
        self.memory_cache.clear()
        
        # Xóa tất cả file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception:
                pass
    
    def cleanup_expired(self):
        """Dọn dẹp các cache đã hết hạn"""
        # Dọn memory cache
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if not self._is_valid(item)
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Dọn file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    item = json.load(f)
                
                if not self._is_valid(item):
                    cache_file.unlink()
            except Exception:
                # Nếu không đọc được, xóa luôn
                try:
                    cache_file.unlink()
                except Exception:
                    pass


def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator để cache kết quả function
    
    Args:
        ttl: Thời gian sống cache (giây)
        key_func: Function để tạo cache key từ args (None = tự động)
    
    Ví dụ:
        @cached(ttl=3600)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result
    """
    cache = SmartCache(default_ttl=ttl)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Tạo cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Tự động tạo key từ args và kwargs
                key_parts = [str(arg) for arg in args]
                key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                cache_key = f"{func.__name__}:{':'.join(key_parts)}"
            
            # Kiểm tra cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Thực thi function và cache kết quả
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Thêm method để invalidate cache
        wrapper.invalidate_cache = lambda *args, **kwargs: cache.invalidate(
            key_func(*args, **kwargs) if key_func else f"{func.__name__}:{':'.join([str(arg) for arg in args])}"
        )
        
        return wrapper
    
    return decorator


# Global cache instance
_global_cache = None

def get_cache(ttl: int = 3600) -> SmartCache:
    """Lấy global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = SmartCache(default_ttl=ttl)
    return _global_cache

