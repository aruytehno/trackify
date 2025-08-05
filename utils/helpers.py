import re


def parse_weight(weight_str):
    """Парсинг веса с обработкой разных форматов"""
    if not weight_str:
        return 0.0

    try:
        cleaned = re.sub(r'\s+', '', str(weight_str)).replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0