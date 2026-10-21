import math
import random

import pygame

from circleshape import CircleShape
from constants import (
    ASTEROID_ANGLE_VARIATION,
    ASTEROID_DISTANCE_VARIATION,
    ASTEROID_MIN_RADIUS,
    ASTEROID_VERTEX_RANGE,
    LINE_WIDTH,
)
from logger import log_event


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
        # print(self.angle)
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
        max = midpoint * (1 + variation)
        rand = random.uniform(min, max)
        return rand

    def update_position(self, center: pygame.Vector2) -> None:
        self.center = center
        self.position = self.get_abs_position()


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.rand_vertex = random.randint(*ASTEROID_VERTEX_RANGE)
        self.vertex_list = []
        angle_step = (2 * math.pi) / self.rand_vertex
        print("angle_step: " + str(angle_step))
        for i in range(0, self.rand_vertex):
            current_min = angle_step * i
            self.vertex_list.append(
                RandomPolygonVertex(
                    current_min, current_min + angle_step, self.radius, self.position
                )
            )

    def draw(self, screen: pygame.Surface) -> None:

        pygame.draw.polygon(
            screen, "red", list(map(lambda x: x.position, self.vertex_list)), LINE_WIDTH
        )
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        for x in self.vertex_list:
            x.update_position(self.position)

    def split(self) -> None:
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")
        rand_angle = random.uniform(20, 50)
        ast1_velocity = self.velocity.rotate(rand_angle) * 1.2
        ast2_velocity = self.velocity.rotate(-rand_angle) * 1.2
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        ast1 = Asteroid(self.position[0], self.position[1], new_radius)
        ast1.velocity = ast1_velocity
        ast2 = Asteroid(self.position[0], self.position[1], new_radius)
        ast2.velocity = ast2_velocity
