import openrouteservice as ors
from config import Config

client = ors.Client(key=Config.ORS_API_KEY)

def geocode_address(address):
    try:
        if not address or not isinstance(address, str):
            return None

        geo = client.pelias_search(
            text=f"{address}, Санкт-Петербург",
            focus_point=[30.3155, 59.9386],
            country="RU"
        )
        return geo['features'][0]['geometry']['coordinates'] if geo.get('features') else None
    except Exception as e:
        logger.warning("Geocoding error for address %s: %s", address, str(e))
        return None