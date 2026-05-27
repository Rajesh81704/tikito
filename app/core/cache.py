"""Redis caching layer using Upstash Redis (TLS)."""
import os
import json
import redis
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=os.getenv("REDIS_TLS", "false").lower() == "true",
        decode_responses=True,
        socket_connect_timeout=3,
    )
    redis_client.ping()
except Exception:
    redis_client = None


def cache_get(key: str):
    """Get a value from cache. Returns None if not found or Redis unavailable."""
    if not redis_client:
        return None
    try:
        val = redis_client.get(key)
        if val:
            return json.loads(val)
    except Exception:
        pass
    return None


def cache_set(key: str, value, ttl: int = 300):
    """Set a value in cache with TTL (default 5 minutes)."""
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_delete(key: str):
    """Delete a specific key from cache."""
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except Exception:
        pass


def cache_delete_pattern(pattern: str):
    """Delete all keys matching a pattern."""
    if not redis_client:
        return
    try:
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                redis_client.delete(*keys)
            if cursor == 0:
                break
    except Exception:
        pass


def cached(prefix: str, ttl: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key_parts = [prefix] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)

            result = cache_get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            if result is not None:
                cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
