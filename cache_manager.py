
from functools import wraps
from datetime import datetime, timedelta
from flask_caching import Cache
from app import app
import logging
import time

logger = logging.getLogger(__name__)

# Configure Flask-Caching
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_THRESHOLD': 1000  # Nombre maximum d'items en cache
})

# Statistiques du cache
cache_stats = {
    'hits': 0,
    'misses': 0,
    'total_time_saved': 0
}

def cache_key_prefix():
    """Generate a cache key prefix"""
    return 'smartohada_'

def get_cache_stats():
    """Retourne les statistiques du cache"""
    return {
        'hits': cache_stats['hits'],
        'misses': cache_stats['misses'],
        'hit_ratio': (cache_stats['hits'] / (cache_stats['hits'] + cache_stats['misses'])) * 100 if (cache_stats['hits'] + cache_stats['misses']) > 0 else 0,
        'total_time_saved': round(cache_stats['total_time_saved'], 2)
    }

def timed_cache(timeout=300):
    """Custom decorator for timed caching with monitoring"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Générer une clé de cache unique
            cache_key = f"{cache_key_prefix()}{f.__name__}_{str(args)}_{str(kwargs)}"
            rv = cache.get(cache_key)
            
            if rv is not None:
                # Cache hit
                cache_stats['hits'] += 1
                execution_time = time.time() - start_time
                cache_stats['total_time_saved'] += execution_time
                logger.debug(f"Cache hit for {f.__name__} - {execution_time:.3f}s")
                return rv
                
            # Cache miss
            cache_stats['misses'] += 1
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            
            execution_time = time.time() - start_time
            logger.debug(f"Cache miss for {f.__name__} - {execution_time:.3f}s")
            return rv
            
        return decorated_function
    return decorator

def clear_cache():
    """Vide le cache"""
    cache.clear()
    logger.info("Cache cleared")
