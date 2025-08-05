import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

class Config:
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    ORS_API_KEY = os.getenv('ORS_API_KEY')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SHEET_RANGE = os.getenv('SHEET_RANGE', 'Лист1!A:Z')
    OPTIMIZE_ROUTES = True
    CACHE_EXPIRY = 3600  # 1 час в секундах


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('trackify.log', maxBytes=1000000, backupCount=3),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)