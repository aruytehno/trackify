import math
import openrouteservice as ors
from typing import List, Dict, Optional
from config import Config, logger
from models.route import RoutePoint, Route
from services.geocoder import geocode_address


class RouteOptimizer:
    def __init__(self):
        """Инициализация сервиса оптимизации маршрутов"""
        try:
            self.warehouse_coords = Config.WAREHOUSE_COORDS
            self.client = ors.Client(key=Config.ORS_API_KEY)
            logger.info("RouteOptimizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RouteOptimizer: {str(e)}")
            raise

    def optimize(self, addresses: List[Dict]) -> Dict[int, Route]:
        if not addresses:
            return {}

        points = self._prepare_points(addresses)
        if not points:
            return {}

        # Используем только активные автомобили
        active_vehicles = [v for v in Config.VEHICLES if v.get('active', True)]
        if not active_vehicles:
            return {}

        # Подготовка заданий с учетом временных окон
        jobs = []
        for idx, point in enumerate(points):
            job = {
                'id': idx,
                'location': [point.lon, point.lat],
                'amount': [math.ceil(point.weight)],
                'service': 300  # Время обслуживания в секундах (5 минут)
            }

            # Добавляем временное окно, если указано
            if hasattr(point, 'time_window') and point.time_window:
                job['time_windows'] = [point.time_window]

            jobs.append(job)

        # Подготовка транспортных средств с временными ограничениями
        vehicles = []
        for vehicle in active_vehicles:  # Используем только активные
            vehicle_def = {
                'id': vehicle['id'],
                'profile': 'driving-car',
                'start': [Config.WAREHOUSE_LON, Config.WAREHOUSE_LAT],
                'end': [Config.WAREHOUSE_LON, Config.WAREHOUSE_LAT],
                'capacity': [vehicle['capacity']],
                'time_window': [28800, 64800]
            }
            vehicles.append(vehicle_def)

        try:
            response = self.client.optimization(
                jobs=jobs,
                vehicles=vehicles,
                geometry=True,
                options={'g': True}
            )

            optimized_routes = {}
            for vehicle in response['routes']:
                route_id = vehicle['vehicle']
                optimized_routes[route_id] = Route.from_ors_response(vehicle, points)

                # Добавляем геометрию маршрута для отображения на карте
                optimized_routes[route_id].geometry = vehicle['geometry']

            return optimized_routes
        except Exception as e:
            logger.error(f"Route optimization failed: {str(e)}")
            return {}

    def _prepare_points(self, addresses: List[Dict]) -> List[RoutePoint]:
        points = []
        failed_addresses = 0

        for addr in addresses:
            try:
                # Проверяем наличие обязательных полей
                if not addr.get('address'):
                    logger.warning(f"Skipping address without data: {addr}")
                    continue

                coords = geocode_address(addr['address'])  # Используйте функцию напрямую
                if not coords:
                    logger.warning(f"Geocoding failed for address: {addr['address']}")
                    failed_addresses += 1
                    continue

                # Создаём точку с новыми полями
                point = RoutePoint(
                    company=addr.get('company', 'Без названия'),
                    address=addr['address'],
                    weight=addr.get('weight', 0),
                    lon=coords[0],
                    lat=coords[1],
                    delivery_date=addr.get('delivery_date', ''),
                    manager=addr.get('manager', '')
                )
                points.append(point)

            except Exception as e:
                logger.error(f"Error processing address {addr.get('address')}: {str(e)}", exc_info=True)
                failed_addresses += 1

        if failed_addresses > 0:
            logger.warning(f"Failed to process {failed_addresses} addresses")

        return points