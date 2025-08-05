import math
import openrouteservice as ors
from config import Config
from models.route import RoutePoint, Route
from services.geocoder import Geocoder


class RouteOptimizer:
    def __init__(self):
        self.client = ors.Client(key=Config.ORS_API_KEY)
        self.geocoder = Geocoder()

    def optimize(self, addresses):
        points = []
        for addr in addresses:
            coords = self.geocoder.geocode(addr['address'])
            if coords:
                points.append(RoutePoint(
                    company=addr['company'],
                    address=addr['address'],
                    weight=addr['weight'],
                    lon=coords[0],
                    lat=coords[1]
                ))

        if not points:
            return None

        jobs = [{
            'id': idx,
            'location': [point.lon, point.lat],
            'amount': [math.ceil(point.weight / 100)]
        } for idx, point in enumerate(points)]

        optimized = self.client.optimization(
            jobs=jobs,
            vehicles=[{
                'id': 0,
                'profile': 'driving-car',
                'start': [30.3155, 59.9386],
                'end': [30.3155, 59.9386]
            }],
            geometry=True
        )

        return Route.from_ors_response(optimized, points)