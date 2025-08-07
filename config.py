import os
import sys

from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

class Config:
    USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    ORS_API_KEY = os.getenv('ORS_API_KEY')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SHEET_RANGE = os.getenv('SHEET_RANGE', 'Лист1!A:Z')
    WAREHOUSE_ADDRESS = os.getenv('WAREHOUSE_ADDRESS')
    WAREHOUSE_LAT = float(os.getenv('WAREHOUSE_LAT'))
    WAREHOUSE_LON = float(os.getenv('WAREHOUSE_LON'))
    WAREHOUSE_COORDS = [WAREHOUSE_LAT, WAREHOUSE_LON]  # [lat, lon]

    if not all([WAREHOUSE_ADDRESS, WAREHOUSE_LAT, WAREHOUSE_LON]):
        raise ValueError("Необходимо указать WAREHOUSE_ADDRESS, WAREHOUSE_LAT и WAREHOUSE_LON в .env")
    OPTIMIZE_ROUTES = True
    CACHE_EXPIRY = 3600  # 1 час в секундах
    VEHICLES = [
        {"id": 1, "capacity": 1000, "color": "blue", "icon": "truck"},
        {"id": 2, "capacity": 800, "color": "green", "icon": "truck"},
        {"id": 3, "capacity": 1200, "color": "orange", "icon": "truck"}
    ]

    @staticmethod
    def init_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('trackify.log', encoding='utf-8')
            ]
        )

Config.init_logging()
logger = logging.getLogger(__name__)