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
from polygonshape import LineSegment, PolygonShape, RandomPolygonVertex


class Asteroid(PolygonShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        rand_vertex = random.randint(*ASTEROID_VERTEX_RANGE)
        angle_step = (2 * math.pi) / rand_vertex
        # print("angle_step: " + str(angle_step))
        for i in range(0, rand_vertex):
            current_min = angle_step * i
            self.vertex_list.append(
                RandomPolygonVertex(
                    current_min, current_min + angle_step, self.radius, self.position
                )
            )
        for i in range(0, math.floor(len(self.vertex_list) / 2), 2):
            j = i + 1 if i + 1 < len(self.vertex_list) else 0
            self.line_list.append(
                LineSegment(self.vertex_list[i].position, self.vertex_list[j].position)
            )

    def draw(self, screen: pygame.Surface) -> None:

        pygame.draw.polygon(
            screen, "red", list(map(lambda x: x.position, self.vertex_list)), LINE_WIDTH
        )
        # pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        for x in self.vertex_list:
            x.update_position(self.position)
        self.line_list = []
        for i in range(0, math.floor(len(self.vertex_list))):
            j = i + 1 if i + 1 < len(self.vertex_list) else 0
            self.line_list.append(
                LineSegment(self.vertex_list[i].position, self.vertex_list[j].position)
            )

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
