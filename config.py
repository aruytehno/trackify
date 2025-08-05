import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    ORS_API_KEY = os.getenv('ORS_API_KEY')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SHEET_RANGE = os.getenv('SHEET_RANGE', 'Лист1!A:Z')
    OPTIMIZE_ROUTES = True
    CACHE_EXPIRY = 3600  # 1 час в секундах