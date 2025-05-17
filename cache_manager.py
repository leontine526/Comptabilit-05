
from functools import wraps
from datetime import datetime, timedelta
from flask_caching import Cache
from app import app

# Configure Flask-Caching
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
})

def cache_key_prefix():
    """Generate a cache key prefix"""
    return 'smartohada_'

def timed_cache(timeout=300):
    """Custom decorator for timed caching"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{cache_key_prefix()}{f.__name__}_{str(args)}_{str(kwargs)}"
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator
