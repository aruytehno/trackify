from googleapiclient.discovery import build
from config import Config
from utils.helpers import parse_weight
from utils.validators import validate_date, validate_address

class GoogleSheetsService:
    def __init__(self):
        self.service = build('sheets', 'v4', developerKey=Config.GOOGLE_SHEETS_API_KEY)

    def get_addresses(self):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=Config.SPREADSHEET_ID,
            range=Config.SHEET_RANGE
        ).execute()

        values = result.get('values', [])
        if not values:
            return []

        headers_row = next((row for row in values if row and row[0] == "Название компании"), None)
        if not headers_row:
            return []

        data_start_index = values.index(headers_row) + 1
        addresses = []

        for row in values[data_start_index:]:
            if not row or len(row) <= 1 or not row[1].strip():
                continue

            try:
                addresses.append({
                    'company': row[0] if len(row) > 0 and row[0] else 'Без названия',
                    'address': row[1].strip(),
                    'weight': parse_weight(row[5] if len(row) > 5 else 0),
                    'delivery_date': row[6] if len(row) > 6 else '',
                    'manager': row[8] if len(row) > 8 else '',
                    'is_valid': validate_address(row[1].strip()) and validate_date(row[6] if len(row) > 6 else '')
                })
            except Exception as e:
                print(f"Ошибка обработки строки: {row}. Ошибка: {str(e)}")
                continue

        return addresses