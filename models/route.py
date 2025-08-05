from dataclasses import dataclass
from typing import List


@dataclass
class RoutePoint:
    company: str
    address: str
    weight: float
    lon: float
    lat: float


class Route:
    def __init__(self, points: List[RoutePoint], geometry):
        self.points = points
        self.geometry = geometry

    @classmethod
    def from_ors_response(cls, response, original_points):
        points = []
        for step in response['routes'][0]['steps']:
            if step['type'] == 'job':
                point = original_points[step['job']]
                points.append(point)

        return cls(
            points=points,
            geometry=response['routes'][0]['geometry']
        )