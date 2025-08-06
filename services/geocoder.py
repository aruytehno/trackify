import openrouteservice as ors
from config import Config

client = ors.Client(key=Config.ORS_API_KEY)

def geocode_address(address):
    try:
        geo = client.pelias_search(
            text=f"{address}, Санкт-Петербург",
            focus_point=[30.3155, 59.9386],
            country="RU"
        )
        return geo['features'][0]['geometry']['coordinates'] if geo['features'] else None
    except Exception:
        return None