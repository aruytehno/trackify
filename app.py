import folium
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


def create_map(center_coords: List[float]) -> folium.Map:
    """Создает базовую карту Folium с настройками"""
    return folium.Map(
        location=center_coords,
        zoom_start=12,
        width='100%',
        height='90vh',
        tiles='OpenStreetMap'
    )


def add_warehouse_marker(map_obj: folium.Map, coords: List[float], address: str) -> None:
    """Добавляет маркер склада на карту"""
    folium.Marker(
        location=coords,
        popup=f"<b>Склад</b><br>{address}",
        icon=folium.Icon(color='green', icon='warehouse', prefix='fa')
    ).add_to(map_obj)


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

        # Создаем карту
        m = create_map(warehouse_coords)
        add_warehouse_marker(m, warehouse_coords, warehouse_address)

        # Обрабатываем адреса доставки
        valid_addresses, success_count = process_delivery_addresses()

        # Оптимизируем маршруты для всех автомобилей
        optimizer = RouteOptimizer()
        optimized_routes = optimizer.optimize(valid_addresses)

        # Собираем все координаты для автоматического масштабирования
        all_coords = [warehouse_coords]
        route_colors = {v['id']: v['color'] for v in Config.VEHICLES}

        # Добавляем маршруты и маркеры на карту
        route_details = {}
        for vehicle_id, route in optimized_routes.items():
            color = route_colors.get(vehicle_id, 'gray')

            # Сохраняем точки маршрута для JS
            route_points = []
            for point in route.points:
                coords = [point.lat, point.lon]
                route_points.append({
                    'lat': point.lat,
                    'lon': point.lon,
                    'popup': f"<b>{point.company}</b><br>{point.address}",
                    'weight': point.weight
                })
                all_coords.append(coords)

            # Добавляем линию маршрута
            folium.PolyLine(
                locations=[(point.lat, point.lon) for point in route.points],
                color=color,
                weight=5,
                opacity=0.7,
                popup=f"Автомобиль {vehicle_id}",
                tooltip=f"Маршрут {vehicle_id}"
            ).add_to(m)

            # Добавляем маркеры для этого маршрута
            for point in route.points:
                folium.Marker(
                    location=[point.lat, point.lon],
                    popup=f"<b>{point.company}</b><br>{point.address}<br>Автомобиль: {vehicle_id}",
                    icon=folium.Icon(color=color, icon='truck', prefix='fa')
                ).add_to(m)

            route_details[vehicle_id] = {
                'color': color,
                'points': route_points,
                'total_weight': sum(p.weight for p in route.points),
                'stops_count': len(route.points)
            }

        # Автоматическое масштабирование под все точки
        if len(all_coords) > 1:
            m.fit_bounds(all_coords)

        logger.info(f"Map generated with {success_count} delivery points across {len(optimized_routes)} vehicles")

        map_html = m.get_root().render()

        return render_template(
            'index.html',
            # map_html=m.get_root().render(),  # Убрать эту строку
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