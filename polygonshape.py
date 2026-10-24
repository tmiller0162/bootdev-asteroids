import random
from itertools import combinations

import pygame

from circleshape import CircleShape
from constants import ASTEROID_ANGLE_VARIATION, ASTEROID_DISTANCE_VARIATION


class RandomPolygonVertex:
    def __init__(
        self,
        angle_start: float,
        angle_end: float,
        radius: float,
        center: pygame.Vector2,
    ) -> None:
        self.angle = self.get_random_in_range(
            angle_start, angle_end, ASTEROID_ANGLE_VARIATION
        )
        self.distance = self.get_random_from_midpoint(
            radius, ASTEROID_DISTANCE_VARIATION
        )
        self.center = center
        self.position = self.get_abs_position()

    def get_abs_position(self) -> pygame.Vector2:
        return self.center + pygame.Vector2(0, 1).rotate_rad(self.angle) * self.distance

    def get_random_in_range(
        self, range_start: float, range_end: float, variation: float
    ) -> float:
        return random.uniform(range_start * variation, range_end * variation)

    # def get_random_in_range(
    #     self, range_start: float, range_end: float, variation: float
    # ) -> float:
    #     range = range_end - range_start
    #     midpoint = (range / 2) + range_start
    #     variation = (range * variation) / (range_end + range_start)
    #     return self.get_random_from_midpoint(midpoint, variation)

    def get_random_from_midpoint(self, midpoint: float, variation: float) -> float:
        min = midpoint * variation
        max = midpoint
        rand = random.uniform(min, max)
        return rand

    def update_position(self, center: pygame.Vector2) -> None:
        self.center = center
        self.position = self.get_abs_position()


class LineSegment:
    def __init__(self, vec_1: pygame.Vector2, vec_2: pygame.Vector2) -> None:
        self.point_1 = vec_1
        self.point_2 = vec_2
        self.min_x = min(vec_1[0], vec_2[0])
        self.min_y = min(vec_1[1], vec_2[1])
        self.max_x = max(vec_1[0], vec_2[0])
        self.max_y = max(vec_1[1], vec_2[1])
        try:
            self.slope = (vec_1[1] - vec_2[1]) / (vec_1[0] - vec_2[0])
            self.y_intercept = vec_1[1] - self.slope * vec_1[0]
        except ZeroDivisionError:
            self.slope = float("inf")
            self.y_intercept = 0 if vec_1[0] == 0 else float("nan")

    def find_intersection(self, other: "LineSegment") -> pygame.Vector2:
        return pygame.Vector2(
            (other.y_intercept - self.y_intercept) / (self.slope - other.slope),
            self.slope
            * ((other.y_intercept - self.y_intercept) / (self.slope - other.slope))
            + self.y_intercept,
        )

    def create_perpendicular(self, point: pygame.Vector2) -> "LineSegment":
        line = LineSegment(pygame.Vector2(1, 1), pygame.Vector2([1, 1]))
        try:
            line.slope = -(1 / self.slope)
            line.y_intercept = point[1] - line.slope * point[0]
        except ZeroDivisionError:
            line.slope = float("inf")
            line.y_intercept = 0 if point[0] == 0 else float("nan")
        line.point_1 = point
        line.point_2 = self.find_intersection(line)
        line.min_x = min(line.point_1[0], line.point_2[0])
        line.min_y = min(line.point_1[1], line.point_2[1])
        line.max_x = max(line.point_1[0], line.point_2[0])
        line.max_y = max(line.point_1[1], line.point_2[1])
        return line

    def is_on_segment(self, point_on_line: pygame.Vector2) -> bool:
        return (
            self.min_x <= point_on_line[0]
            and self.max_x >= point_on_line[0]
            and self.min_y <= point_on_line[1]
            and self.max_y >= point_on_line[1]
        )

    def collides_with(self, other: "LineSegment") -> bool:
        def triangle_area(
            a: pygame.Vector2, b: pygame.Vector2, c: pygame.Vector2
        ) -> float:
            return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])

        return (triangle_area(self.point_1, self.point_2, other.point_1) > 0) ^ (
            triangle_area(self.point_1, self.point_2, other.point_2) > 0
        ) and (
            (triangle_area(other.point_1, other.point_2, self.point_1) > 0)
            ^ (triangle_area(other.point_1, other.point_2, self.point_2) > 0)
        )


class PolygonShape(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.vertex_list = []
        self.line_list = []

    def collides_with(self, other: "PolygonShape | CircleShape") -> bool:
        if isinstance(other, PolygonShape):
            for line_a in self.line_list:
                for line_b in other.line_list:
                    if line_a.collides_with(line_b):
                        return True
            return False
        elif isinstance(other, CircleShape):
            points = self.vertex_list
            lines = self.line_list
            # lines = map(lambda x: LineSegment(x[0], x[1]), combinations(points, 2))
            if self.position.distance_to(other.position) > self.radius + other.radius:
                return False
            for line in lines:
                perp_line = line.create_perpendicular(other.position)
                intersect_point = line.find_intersection(perp_line)
                if (
                    line.is_on_segment(intersect_point)
                    and other.position.distance_to(intersect_point) < other.radius
                ):
                    return True
                    # pass
            for point in points:
                if point.position.distance_to(other.position) < other.radius:
                    return True
            return False
