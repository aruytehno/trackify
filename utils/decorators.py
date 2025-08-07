import time
import pickle
import os
from functools import wraps
from config import Config
from collections import OrderedDict


class GeocodeCache:
    def __init__(self, max_size=1000, cache_file="geocode_cache.pkl"):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.cache_file = cache_file
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    self.cache = pickle.load(f)
            except (pickle.PickleError, FileNotFoundError):
                self.cache = OrderedDict()

    def _save_cache(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)

    def get(self, address):
        if address in self.cache:
            entry = self.cache[address]
            if time.time() - entry["timestamp"] < Config.CACHE_EXPIRY:
                # Обновляем порядок использования (LRU)
                self.cache.move_to_end(address)
                return entry["result"]
        return None

    def set(self, address, result):
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Удаляем самый старый элемент
        self.cache[address] = {"result": result, "timestamp": time.time()}
        self._save_cache()


# Глобальный кеш
geocode_cache = GeocodeCache()


def cache_geocode(func):
    @wraps(func)
    def wrapper(address):
        cached_result = geocode_cache.get(address)
        if cached_result is not None:
            return cached_result

        result = func(address)
        if result is not None:
            geocode_cache.set(address, result)
        return result

    return wrapper