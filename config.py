import os
import sys

from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

class Config:
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    ORS_API_KEY = os.getenv('ORS_API_KEY')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SHEET_RANGE = os.getenv('SHEET_RANGE', 'Лист1!A:Z')
    WAREHOUSE_ADDRESS = os.getenv('WAREHOUSE_ADDRESS')
    WAREHOUSE_LAT = float(os.getenv('WAREHOUSE_LAT'))
    WAREHOUSE_LON = float(os.getenv('WAREHOUSE_LON'))
    WAREHOUSE_COORDS = [WAREHOUSE_LAT, WAREHOUSE_LON]  # Для Folium [lat, lon]

    if not all([WAREHOUSE_ADDRESS, WAREHOUSE_LAT, WAREHOUSE_LON]):
        raise ValueError("Необходимо указать WAREHOUSE_ADDRESS, WAREHOUSE_LAT и WAREHOUSE_LON в .env")
    OPTIMIZE_ROUTES = True
    CACHE_EXPIRY = 3600  # 1 час в секундах


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