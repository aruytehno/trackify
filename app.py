import os
from flask import Flask, jsonify
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Конфигурация
API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1E6dR_afitz_gDb10eFgqwrBmihuLeAgC43Wgrxvejw4')
SHEET_RANGE = os.getenv('SHEET_RANGE', 'Лист1!A:Z')


def get_google_sheets_data():
    """Получает и обрабатывает данные из Google Sheets"""
    try:
        service = build('sheets', 'v4', developerKey=API_KEY)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()

        values = result.get('values', [])

        if not values:
            return {'error': 'Данные не найдены'}, 404

        # Определяем строку с настоящими заголовками (строка с "Название компании")
        headers_row = None
        for row in values:
            if row and row[0] == "Название компании":
                headers_row = row
                break

        if not headers_row:
            return {'error': 'Не найдена строка с заголовками'}, 400

        # Определяем индекс начала данных (строка после заголовков)
        data_start_index = values.index(headers_row) + 1

        # Обрабатываем данные
        processed_data = []
        drivers = set()

        for row in values[data_start_index:]:
            if not row or not any(cell.strip() for cell in row):
                continue  # Пропускаем пустые строки

            # Создаем словарь для строки
            item = {}
            for i, header in enumerate(headers_row):
                if i < len(row):
                    item[header.strip()] = row[i].strip()
                else:
                    item[header.strip()] = ""

            # Добавляем водителя если есть соответствующее поле
            if 'Водитель' in item and item['Водитель']:
                drivers.add(item['Водитель'])
            elif 'Иван' in item and item['Иван']:  # Альтернативное название поля
                drivers.add(item['Иван'])

            processed_data.append(item)

        return {
            'headers': headers_row,
            'data': processed_data,
            'drivers': sorted(drivers),
            'total_entries': len(processed_data)
        }, 200

    except Exception as e:
        print(f"Ошибка при получении данных: {str(e)}")
        return {'error': str(e)}, 500


@app.route('/api/data', methods=['GET'])
def get_data():
    """API endpoint для получения данных"""
    response, status_code = get_google_sheets_data()
    return jsonify(response), status_code


@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    """API endpoint для получения списка водителей"""
    response, status_code = get_google_sheets_data()
    if status_code != 200:
        return jsonify(response), status_code
    return jsonify({'drivers': response['drivers']})


@app.route('/api/driver/<name>', methods=['GET'])
def get_driver_data(name):
    """API endpoint для получения данных по конкретному водителю"""
    response, status_code = get_google_sheets_data()
    if status_code != 200:
        return jsonify(response), status_code

    driver_data = []
    for item in response['data']:
        if ('Водитель' in item and item['Водитель'].lower() == name.lower()) or \
                ('Иван' in item and item['Иван'].lower() == name.lower()):
            driver_data.append(item)

    return jsonify({
        'driver': name,
        'orders': driver_data,
        'count': len(driver_data)
    })


@app.route('/')
def index():
    """Главная страница с документацией API"""
    return """
    <h1>Сервис управления маршрутами</h1>
    <h2>Доступные API endpoints:</h2>
    <ul>
        <li><a href="/api/data">/api/data</a> - все данные из таблицы</li>
        <li><a href="/api/drivers">/api/drivers</a> - список всех водителей</li>
        <li>/api/driver/&lt;name&gt; - данные по конкретному водителю</li>
    </ul>
    """


if __name__ == '__main__':
    app.run(debug=True, port=5000)