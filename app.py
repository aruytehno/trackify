from flask import Flask, render_template
from config import Config
from services.route_optimizer import RouteOptimizer
from services.sheets import get_addresses
from services.geocoder import geocode_address
import logging
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def process_delivery_addresses() -> tuple[List[Dict[str, Any]], int]:
    """Обрабатывает адреса доставки и возвращает список валидных адресов и их количество"""
    valid_addresses = []
    success_count = 0

    addresses = get_addresses()
    logger.info(f"Total addresses from Google Sheets: {len(addresses)}")

    for address in addresses:
        if not address.get('address'):
            continue

        coords = geocode_address(address['address'])
        if coords:
            logger.info(f"Geocoded address: {address['address']} -> {coords}")
            address['coords'] = coords
            valid_addresses.append(address)
            success_count += 1
        else:
            logger.warning(f"Failed to geocode address: {address.get('address')}")

    return valid_addresses, success_count


@app.route('/')
def index():
    try:
        # Получаем данные склада из конфига
        warehouse_coords = Config.WAREHOUSE_COORDS
        warehouse_address = Config.WAREHOUSE_ADDRESS

        # Обрабатываем адреса доставки
        valid_addresses, success_count = process_delivery_addresses()

        # Оптимизируем маршруты
        optimizer = RouteOptimizer()
        optimized_routes = optimizer.optimize(valid_addresses)

        # Подготавливаем данные о маршрутах для шаблона
        route_details = {}
        for vehicle_id, route in optimized_routes.items():
            color = next(
                (v['color'] for v in Config.VEHICLES if v['id'] == vehicle_id),
                'gray'
            )

            # Подготавливаем данные о маршрутах для шаблона
            route_details = {}
            for vehicle_id, route in optimized_routes.items():
                color = next(
                    (v['color'] for v in Config.VEHICLES if v['id'] == vehicle_id),
                    'gray'
                )

                route_points = []
                for point in route.points:
                    route_points.append({
                        'lat': point.lat,
                        'lon': point.lon,
                        'popup': f"<b>{point.company}</b><br>{point.address}",
                        'weight': point.weight
                    })

                route_details[vehicle_id] = {
                    'color': color,
                    'points': route_points,
                    'total_weight': sum(p.weight for p in route.points),
                    'stops_count': len(route.points),
                    'geometry': route.geometry  # Добавляем геометрию маршрута
                }

        logger.info(f"Generated routes for {success_count} delivery points across {len(optimized_routes)} vehicles")

        return render_template(
            'index.html',
            warehouse_address=warehouse_address,
            addresses=valid_addresses,
            vehicles=Config.VEHICLES,
            routes=route_details,
            coordinates_json={
                'warehouse': {
                    'lat': warehouse_coords[0],
                    'lon': warehouse_coords[1],
                    'popup': f"<b>Склад</b><br>{warehouse_address}"
                },
                'deliveries': [
                    {
                        'lat': addr['coords'][0],
                        'lon': addr['coords'][1],
                        'popup': f"<b>{addr.get('company', 'Без названия')}</b><br>{addr['address']}"
                    }
                    for addr in valid_addresses
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error in index route: {str(e)}", exc_info=True)
        return render_template(
            'error.html',
            error_message="Произошла ошибка при загрузке карты"
        ), 500


if __name__ == '__main__':
    logger.info("Starting Trackify application")
    app.run(host='0.0.0.0', port=5000, debug=False)