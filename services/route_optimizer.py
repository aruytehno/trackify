import math
import openrouteservice as ors
from typing import List, Dict, Optional
from config import Config, logger
from models.route import RoutePoint, Route
from services.geocoder import Geocoder


class RouteOptimizer:
    def __init__(self):
        """Инициализация сервиса оптимизации маршрутов"""
        try:
            self.client = ors.Client(key=Config.ORS_API_KEY)
            self.geocoder = Geocoder()
            logger.info("RouteOptimizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RouteOptimizer: {str(e)}")
            raise

    def optimize(self, addresses: List[Dict]) -> Optional[Route]:
        """
        Оптимизирует маршрут для заданных адресов

        Args:
            addresses: Список адресов в формате:
                [
                    {
                        'company': str,
                        'address': str,
                        'weight': float,
                        ...
                    },
                    ...
                ]

        Returns:
            Route: Оптимизированный маршрут или None в случае ошибки
        """
        if not addresses:
            logger.warning("Empty addresses list received")
            return None

        logger.info(f"Starting route optimization for {len(addresses)} addresses")

        try:
            points = self._prepare_points(addresses)
            if not points:
                return None

            optimized_route = self._get_optimized_route(points)
            if not optimized_route:
                return None

            return Route.from_ors_response(optimized_route, points)

        except ors.exceptions.ApiError as api_err:
            logger.error(f"ORS API error: {api_err.status_code} - {api_err.message}")
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")

        return None

    def _prepare_points(self, addresses: List[Dict]) -> List[RoutePoint]:
        """Подготавливает точки маршрута с геокодированием"""
        points = []
        failed_addresses = 0

        for addr in addresses:
            try:
                coords = self.geocoder.geocode(addr['address'])
                if not coords:
                    failed_addresses += 1
                    continue

                points.append(RoutePoint(
                    company=addr.get('company', 'Без названия'),
                    address=addr['address'],
                    weight=addr.get('weight', 0),
                    lon=coords[0],
                    lat=coords[1],
                    delivery_date=addr.get('delivery_date', ''),
                    manager=addr.get('manager', '')
                ))
            except Exception as e:
                logger.warning(f"Failed to process address {addr.get('address')}: {str(e)}")
                failed_addresses += 1

        if failed_addresses > 0:
            logger.warning(f"Failed to geocode {failed_addresses} addresses")

        return points

    def _get_optimized_route(self, points: List[RoutePoint]) -> Optional[Dict]:
        """Получает оптимизированный маршрут из ORS API"""
        try:
            jobs = [{
                'id': idx,
                'location': [point.lon, point.lat],
                'amount': [math.ceil(point.weight / 100)],
                'service': 300  # Время обслуживания точки в секундах (5 мин)
            } for idx, point in enumerate(points)]

            return self.client.optimization(
                jobs=jobs,
                vehicles=[{
                    'id': 0,
                    'profile': 'driving-car',
                    'start': [30.3155, 59.9386],  # Координаты склада
                    'end': [30.3155, 59.9386],
                    'capacity': [100],  # Грузоподъемность (в условных единицах)
                    'time_window': [28800, 64800]  # Временное окно (8:00-18:00)
                }],
                geometry=True,
                options={
                    'g': True,  # Включаем геометрию маршрута
                },
                matrix_options={
                    'profile': 'driving-car'
                }
            )
        except Exception as e:
            logger.error(f"Route optimization failed: {str(e)}")
            return None