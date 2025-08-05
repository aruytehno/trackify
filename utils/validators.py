import re
from datetime import datetime

def validate_date(date_str):
    """Проверяет формат даты (дд.мм или дд.мм - дд.мм)"""
    if not date_str:
        return False
    pattern = r'^\d{1,2}\.\d{1,2}(?:\s*-\s*\d{1,2}\.\d{1,2})?$'
    return bool(re.match(pattern, date_str))

def validate_address(address):
    """Проверяет, что адрес содержит минимально необходимую информацию"""
    return address and len(address.strip()) > 5 and any(char.isdigit() for char in address)