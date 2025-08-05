from flask import Flask, jsonify, Response
import json
from services.sheets import GoogleSheetsService
from services.route_optimizer import RouteOptimizer
from config import Config

app = Flask(__name__)

sheets_service = GoogleSheetsService()
route_optimizer = RouteOptimizer()


@app.route('/api/addresses', methods=['GET'])
def api_addresses():
    addresses = sheets_service.get_addresses()
    return json_response(addresses)


@app.route('/api/optimize', methods=['GET'])
def api_optimize():
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
                'lat': p.lat
            } for p in route.points],
            'geometry': route.geometry
        })
    else:
        return json_response({'addresses': addresses})


@app.route('/api/map', methods=['GET'])
def api_map():
    route_data = api_optimize().get_json()
    if 'error' in route_data:
        return json_response(route_data, 400)

    try:
        # Создаем карту
        m = folium.Map(location=[59.9386, 30.3155], zoom_start=12)

        # Добавляем маршрут
        if 'geometry' in route_data:
            decoded = ors.convert.decode_polyline(route_data['geometry'])
            folium.PolyLine(
                locations=[(p[1], p[0]) for p in decoded['coordinates']],
                color='blue',
                weight=5
            ).add_to(m)

        # Добавляем точки маршрута
        for idx, point in enumerate(route_data.get('points', [])):
            folium.Marker(
                location=[point['lat'], point['lon']],
                popup=f"<b>{point['company']}</b><br>{point['address']}",
                tooltip=f"{idx + 1}. {point['company']}",
                icon=folium.Icon(color='red' if idx == 0 else 'blue')
            ).add_to(m)

        # Добавляем стартовую точку (склад)
        folium.Marker(
            location=[59.9386, 30.3155],
            popup="<b>Склад</b>",
            icon=folium.Icon(color='green', icon='warehouse')
        ).add_to(m)

        return m._repr_html_()

    except Exception as e:
        return json_response({'error': f'Ошибка создания карты: {str(e)}'}, 500)

def json_response(data, status_code=200):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)