from config import Config, logger
import openrouteservice as ors
from utils.decorators import cache_geocode

client = ors.Client(key=Config.ORS_API_KEY)

@cache_geocode
def geocode_address(address):
    """Геокодирование адреса с поддержкой мок-данных и кэширования."""
    if not address:
        return None

    # Проверка мок-режима
    if Config.USE_MOCK_DATA:
        address_lower = address.lower()
        if address_lower in MOCK_GEOCODE_DATA:
            logger.debug(f"Используются мок-данные для адреса: {address}")
            return MOCK_GEOCODE_DATA[address_lower]
        else:
            logger.warning(f"Адрес не найден в мок-данных: {address}")
            return [59.934280, 30.335099]  # Координаты по умолчанию (центр СПб)

    # Реальный запрос к ORS API
    try:
        geo = client.pelias_search(
            text=f"{address}, {Config.WAREHOUSE_ADDRESS.split(',')[0].strip()}",
            focus_point=[Config.WAREHOUSE_LON, Config.WAREHOUSE_LAT],
            country="RU"
        )

        if not geo.get('features'):
            logger.warning(f"Адрес не найден в ORS: {address}")
            return None

        # Конвертация координат [lon, lat] → [lat, lon]
        coords = geo['features'][0]['geometry']['coordinates']
        return [coords[1], coords[0]]

    except ors.exceptions.ApiError as e:
        logger.error(f"ORS API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка геокодирования: {address} - {str(e)}")
        return None