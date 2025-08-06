from config import Config, logger
import openrouteservice as ors
from utils.decorators import cache_geocode

client = ors.Client(key=Config.ORS_API_KEY)

@cache_geocode
def geocode_address(address):
    try:
        if not address:
            return None

        geo = client.pelias_search(
            text=f"{address}, {Config.WAREHOUSE_ADDRESS.split(',')[0].strip()}",
            focus_point=[Config.WAREHOUSE_LON, Config.WAREHOUSE_LAT],  # ORS ожидает [lon, lat]
            country="RU"
        )

        if not geo.get('features'):
            logger.warning(f"Адрес не найден: {address}")
            return None

        # Конвертируем ORS [lon, lat] → Folium [lat, lon]
        coords = geo['features'][0]['geometry']['coordinates']
        return [coords[1], coords[0]]

    except Exception as e:
        logger.error(f"Ошибка геокодирования: {address} - {str(e)}")
        return None