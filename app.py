import os
from flask import Flask, jsonify, request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import openrouteservice as ors
from openrouteservice import convert
import folium
import math

load_dotenv()

app = Flask(__name__)

# Конфигурация
API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
ORS_API_KEY = os.getenv('ORS_API_KEY')  # Ключ OpenRouteService
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SHEET_RANGE = os.getenv('SHEET_RANGE', 'Лист1!A:Z')
OPTIMIZE_ROUTES = True  # Флаг оптимизации маршрутов

# Инициализация клиента ORS
ors_client = ors.Client(key=ORS_API_KEY)


def get_sheet_data():
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

        # Находим строку с заголовками
        headers_row = next((row for row in values if row and row[0] == "Название компании"), None)
        if not headers_row:
            return {'error': 'Не найдена строка с заголовками'}, 400

        data_start_index = values.index(headers_row) + 1
        addresses = []

        for row in values[data_start_index:]:
            if not row or len(row) <= 1 or not row[1].strip():
                continue

            try:
                address = {
                    'company': row[0] if len(row) > 0 else '',
                    'address': row[1],
                    'weight': float(row[5]) if len(row) > 5 and row[5] else 0,
                    'delivery_date': row[6] if len(row) > 6 else '',
                    'manager': row[8] if len(row) > 8 else ''
                }
                addresses.append(address)
            except (IndexError, ValueError) as e:
                print(f"Ошибка обработки строки: {row}. Ошибка: {str(e)}")
                continue

        return {'addresses': addresses}, 200

    except Exception as e:
        print(f"Ошибка при получении данных: {str(e)}")
        return {'error': str(e)}, 500


def optimize_routes(addresses):
    """Оптимизирует маршруты с помощью ORS API"""
    try:
        # Геокодирование адресов
        locations = []
        for addr in addresses:
            try:
                geo = ors_client.pelias_search(
                    text=addr['address'] + ', Санкт-Петербург',
                    focus_point=[30.3155, 59.9386],  # Центр СПб
                    boundary={'country': "RU"}  # Исправленный параметр
                )
                if geo['features']:
                    coords = geo['features'][0]['geometry']['coordinates']
                    locations.append({
                        'coordinates': coords,
                        'properties': addr
                    })
            except Exception as e:
                print(f"Ошибка геокодирования адреса {addr['address']}: {str(e)}")
                continue

        if not locations:
            return {'error': 'Не удалось геокодировать адреса'}, 400

        # Подготовка точек для оптимизации
        coords = [loc['coordinates'] for loc in locations]

        # Оптимизация маршрута
        optimized = ors_client.optimization(
            jobs=[{
                'id': idx,
                'location': loc['coordinates'],
                'amount': [math.ceil(loc['properties']['weight'] / 100)]
            } for idx, loc in enumerate(locations)],
            vehicles=[{
                'id': 0,
                'profile': 'driving-car',
                'start': [30.3155, 59.9386],
                'end': [30.3155, 59.9386]
            }],
            options={'g': True}
        )

        # Формирование результата
        routes = []
        for step in optimized['routes'][0]['steps']:
            if step['type'] == 'job':
                loc_idx = step['job']
                routes.append(locations[loc_idx]['properties'])

        return {'optimized_route': routes}, 200

    except Exception as e:
        print(f"Ошибка оптимизации маршрута: {str(e)}")
        return {'error': str(e)}, 500


import json
from flask import Response


# Доработка функции get_addresses():
@app.route('/api/addresses', methods=['GET'])
def get_addresses():
    """Получение списка адресов в читаемом формате"""
    response, status_code = get_sheet_data()

    if status_code != 200:
        return jsonify(response), status_code

    # Формируем красиво отформатированный JSON с кириллицей
    human_readable = json.dumps(
        response,
        ensure_ascii=False,  # Это ключевой параметр для кириллицы
        indent=2,  # Добавляем отступы для читаемости
        sort_keys=True  # Сортируем ключи для порядка
    )

    return Response(
        human_readable,
        mimetype='application/json; charset=utf-8'
    )


# Аналогично можно доработать другие endpoint'ы:
@app.route('/api/optimize', methods=['GET'])
def optimize():
    """Оптимизация маршрутов с читаемым выводом"""
    response, status_code = get_sheet_data()
    if status_code != 200:
        return jsonify(response), status_code

    if OPTIMIZE_ROUTES:
        result, status_code = optimize_routes(response['addresses'])
        if status_code != 200:
            return jsonify(result), status_code

        human_readable = json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            sort_keys=True
        )
        return Response(human_readable, mimetype='application/json; charset=utf-8')
    else:
        human_readable = json.dumps(
            {'addresses': response['addresses']},
            ensure_ascii=False,
            indent=2,
            sort_keys=True
        )
        return Response(human_readable, mimetype='application/json; charset=utf-8')


@app.route('/api/map', methods=['GET'])
def show_map():
    """Визуализация маршрута на карте"""
    response, status_code = optimize()
    if status_code != 200:
        return jsonify(response), status_code

    try:
        # Создаем карту с центром в СПб
        m = folium.Map(location=[59.9386, 30.3155], zoom_start=12)

        # Добавляем маркеры для каждого адреса
        for idx, addr in enumerate(response['optimized_route']):
            folium.Marker(
                location=[addr.get('lat', 0), addr.get('lon', 0)],
                popup=f"{idx + 1}. {addr['company']} - {addr['address']}",
                icon=folium.Icon(color='red' if idx == 0 else 'blue')
            ).add_to(m)

        # Возвращаем HTML с картой
        return m._repr_html_()

    except Exception as e:
        print(f"Ошибка создания карты: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    """Главная страница с документацией API"""
    return """
    <h1>Система оптимизации маршрутов доставки</h1>
    <h2>Доступные API endpoints:</h2>
    <ul>
        <li><a href="/api/addresses">/api/addresses</a> - список адресов</li>
        <li><a href="/api/optimize">/api/optimize</a> - оптимизированный маршрут</li>
        <li><a href="/api/map">/api/map</a> - визуализация маршрута на карте</li>
    </ul>
    """


if __name__ == '__main__':
    app.run(debug=True, port=5000)