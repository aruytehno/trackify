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


def json_response(data, status_code=200):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)