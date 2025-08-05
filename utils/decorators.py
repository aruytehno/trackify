from functools import wraps
import time
from config import Config


def cache_geocode(func):
    """Декоратор для кэширования результатов геокодирования"""
    cache = {}

    @wraps(func)
    def wrapper(address):
        if address in cache:
            cached = cache[address]
            if time.time() - cached['timestamp'] < Config.CACHE_EXPIRY:
                return cached['result']

        result = func(address)
        cache[address] = {
            'result': result,
            'timestamp': time.time()
        }
        return result

    return wrapper