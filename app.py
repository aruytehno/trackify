from flask import Flask, jsonify, Response, render_template_string
import json
from services.sheets import GoogleSheetsService
from services.route_optimizer import RouteOptimizer
from config import Config, logger

app = Flask(__name__)

sheets_service = GoogleSheetsService()
route_optimizer = RouteOptimizer()

# HTML шаблон для главной страницы
INDEX_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Trackify - Оптимизация маршрутов</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        .endpoint { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 10px;
        }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .connected { color: green; }
        .disconnected { color: red; }
    </style>
</head>
<body>
    <h1>Trackify - Система оптимизации маршрутов</h1>

    <div class="endpoint">
        <h3>Доступные API endpoints:</h3>
        <ul>
            <li><a href="/api/addresses">/api/addresses</a> - список адресов</li>
            <li><a href="/api/optimize">/api/optimize</a> - оптимизированный маршрут</li>
            <li><a href="/api/map">/api/map</a> - визуализация маршрута на карте</li>
        </ul>
    </div>

    <div class="endpoint">
        <h3>Статус системы:</h3>
        <p>Google Sheets: <span class="{{ sheets_class }}">{{ sheets_status }}</span></p>
        <p>OpenRouteService: <span class="{{ ors_class }}">{{ ors_status }}</span></p>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Главная страница с документацией API"""
    sheets_ok = check_sheets_connection()
    ors_ok = check_ors_connection()

    return render_template_string(
        INDEX_HTML,
        sheets_status="✓ подключено" if sheets_ok else "✗ ошибка",
        sheets_class="connected" if sheets_ok else "disconnected",
        ors_status="✓ подключено" if ors_ok else "✗ ошибка",
        ors_class="connected" if ors_ok else "disconnected"
    )



@app.route('/api/addresses', methods=['GET'])
def api_addresses():
    """Получение списка адресов"""
    addresses = sheets_service.get_addresses()
    return json_response(addresses)


@app.route('/api/optimize', methods=['GET'])
def api_optimize():
    """Оптимизация маршрутов"""
    addresses = sheets_service.get_addresses()
    if not addresses:
        return json_response({'error': 'Нет данных для оптимизации'}, 400)

    if Config.OPTIMIZE_ROUTES:
        route = route_optimizer.optimize(addresses)
        if not route:
            return json_response({'error': 'Не удалось оптимизировать маршрут'}, 400)

        return json_response({
            'points': [{
                'company': p.company,
                'address': p.address,
                'weight': p.weight,
                'lon': p.lon,
                'lat': p.lat,
                'delivery_date': p.delivery_date,
                'manager': p.manager
            } for p in route.points],
            'geometry': route.geometry
        })
    else:
        return json_response({'addresses': addresses})


@app.route('/api/map', methods=['GET'])
def api_map():
    """Визуализация маршрута на карте"""
    from flask import request
    from io import BytesIO
    import base64
    import folium
    import openrouteservice as ors

    # Получаем данные оптимизации
    optimize_response = api_optimize()
    if optimize_response.status_code != 200:
        return optimize_response

    route_data = optimize_response.get_json()

    try:
        # Создаем карту
        m = folium.Map(location=[59.9386, 30.3155], zoom_start=12)

        # Добавляем маршрут
        if 'geometry' in route_data:
            decoded = ors.convert.decode_polyline(route_data['geometry'])
            folium.PolyLine(
                locations=[(p[1], p[0]) for p in decoded['coordinates']],
                color='blue',
                weight=5,
                opacity=0.7
            ).add_to(m)

        # Добавляем точки маршрута
        for idx, point in enumerate(route_data.get('points', [])):
            folium.Marker(
                location=[point['lat'], point['lon']],
                popup=f"<b>{point['company']}</b><br>"
                      f"Адрес: {point['address']}<br>"
                      f"Вес: {point['weight']} кг<br>"
                      f"Дата: {point['delivery_date']}",
                tooltip=f"{idx + 1}. {point['company']}",
                icon=folium.Icon(color='red' if idx == 0 else 'blue')
            ).add_to(m)

        # Добавляем стартовую точку (склад)
        folium.Marker(
            location=[59.9386, 30.3155],
            popup="<b>Склад</b><br>Начало маршрута",
            icon=folium.Icon(color='green', icon='warehouse')
        ).add_to(m)

        # Сохраняем карту в HTML
        map_html = m._repr_html_()
        return map_html

    except Exception as e:
        logger.error(f"Map generation error: {str(e)}")
        return json_response({'error': f'Ошибка создания карты: {str(e)}'}, 500)

def check_sheets_connection():
    """Проверяет подключение к Google Sheets"""
    try:
        data = sheets_service.get_addresses()
        return bool(data)
    except Exception as e:
        logger.error(f"Google Sheets connection error: {str(e)}")
        return False


def check_ors_connection():
    """Проверяет подключение к OpenRouteService"""
    try:
        import openrouteservice as ors
        client = ors.Client(key=Config.ORS_API_KEY)
        response = client.pelias_search(
            text="Дворцовая площадь, Санкт-Петербург",
            focus_point=[30.3155, 59.9386]
        )
        return bool(response.get('features'))
    except Exception as e:
        logger.error(f"OpenRouteService connection error: {str(e)}")
        return False


def json_response(data, status_code=200):
    """Формирует JSON-ответ с правильными заголовками"""
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )


if __name__ == '__main__':
    logger.info("Starting Trackify application")
    app.run(debug=True, port=5000)