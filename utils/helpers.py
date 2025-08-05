import re

from math import radians, sin, cos, sqrt, atan2


def haversine(coord1, coord2):
    # Расчет расстояния между двумя точками в км
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return 6371 * c  # Радиус Земли в км


def parse_weight(weight_str):
    """Парсинг веса с обработкой разных форматов"""
    if not weight_str:
        return 0.0

    try:
        cleaned = re.sub(r'\s+', '', str(weight_str)).replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0