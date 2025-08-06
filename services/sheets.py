from googleapiclient.discovery import build
from config import Config


def get_addresses():
    service = build('sheets', 'v4', developerKey=Config.GOOGLE_SHEETS_API_KEY)
    result = service.spreadsheets().values().get(
        spreadsheetId=Config.SPREADSHEET_ID,
        range=Config.SHEET_RANGE
    ).execute()

    return [
        {'company': row[0], 'address': row[1]}
        for row in result.get('values', [])[1:]  # Пропускаем заголовок
        if len(row) > 1
    ]