"""Redis caching layer using Upstash Redis (TLS)."""
import os
import json
import redis
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=os.getenv("REDIS_TLS", "true").lower() == "true",
    decode_responses=True,
)


def cache_get(key: str):
    """Get a value from cache. Returns None if not found."""
    val = redis_client.get(key)
    if val:
        return json.loads(val)
    return None


def cache_set(key: str, value, ttl: int = 300):
    """Set a value in cache with TTL (default 5 minutes)."""
    redis_client.setex(key, ttl, json.dumps(value, default=str))


def cache_delete(key: str):
    """Delete a specific key from cache."""
    redis_client.delete(key)


def cache_delete_pattern(pattern: str):
    """Delete all keys matching a pattern."""
    cursor = 0
    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
        if keys:
            redis_client.delete(*keys)
        if cursor == 0:
            break


def cached(prefix: str, ttl: int = 300):
    """Decorator to cache function results.
    
    Usage:
        @cached("turfs:city", ttl=600)
        def get_turfs_by_city(city: str):
            ...
    
    Cache key will be: prefix:arg1:arg2:...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from args
            key_parts = [prefix] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)

            # Try cache first
            result = cache_get(cache_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
