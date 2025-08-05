import openrouteservice as ors
from config import Config
from functools import lru_cache

class Geocoder:
    def __init__(self):
        self.client = ors.Client(key=Config.ORS_API_KEY)

    @lru_cache(maxsize=1000)
    def geocode(self, address):
        """Геокодирование адреса с кэшированием"""
        try:
            geo = self.client.pelias_search(
                text=f"{address}, Санкт-Петербург",
                focus_point=[30.3155, 59.9386],
                country="RU"
            )
            return geo['features'][0]['geometry']['coordinates'] if geo['features'] else None
        except Exception as e:
            print(f"Ошибка геокодирования адреса {address}: {str(e)}")
            return None