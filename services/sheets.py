from googleapiclient.discovery import build
from config import Config


def get_addresses():
    try:
        service = build('sheets', 'v4', developerKey=Config.GOOGLE_SHEETS_API_KEY)
        result = service.spreadsheets().values().get(
            spreadsheetId=Config.SPREADSHEET_ID,
            range=Config.SHEET_RANGE
        ).execute()

        rows = result.get('values', [])
        if not rows or len(rows) < 2:  # Проверяем, что есть хотя бы заголовок и одна строка
            return []

        return [
            {'company': row[0] if len(row) > 0 else 'Без названия',
             'address': row[1] if len(row) > 1 else ''}
            for row in rows[1:]  # Пропускаем заголовок
            if len(row) > 1 and row[1].strip()  # Только строки с адресом
        ]
    except Exception as e:
        logger.error("Error fetching data from Google Sheets: %s", str(e))
        return []