import math
from itertools import combinations

import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_RADIUS,
    PLAYER_SHOT_COOLDOWN_SECONDS,
    PLAYER_SHOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    RESPAWN_ANIMATION_INTERVAL,
    RESPAWN_INVINCIBLE_TIMER,
    SHOT_RADIUS,
)
from shot import Shot


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
        return line

    def is_on_segment(self, point_on_line: pygame.Vector2) -> bool:
        return (
            self.min_x <= point_on_line[0]
            and self.max_x >= point_on_line[0]
            and self.min_y <= point_on_line[1]
            and self.max_y >= point_on_line[1]
        )


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_timer = 0
        self.is_invincible = False
        self.alpha = 255

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def collides_with(self, other: "CircleShape") -> bool:
        points = self.triangle()
        lines = map(lambda x: LineSegment(x[0], x[1]), combinations(points, 2))
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
            if point.distance_to(other.position) < other.radius:
                return True
        return False

    def draw(self, screen) -> None:
        lx, ly = zip(*self.triangle())
        min_x, min_y, max_x, max_y = (
            min(lx) - LINE_WIDTH,
            min(ly) - LINE_WIDTH,
            max(lx) + LINE_WIDTH,
            max(ly) + LINE_WIDTH,
        )
        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, "red", target_rect)
        pygame.draw.polygon(
            shape_surf,
            (255, 255, 255, int(self.alpha)),
            [(x - min_x, y - min_y) for x, y in self.triangle()],
            # self.triangle(),
            LINE_WIDTH,
        )
        screen.blit(shape_surf, target_rect)

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt: float) -> None:
        unit_vector = pygame.Vector2(0, 1)
        rotated_vec = unit_vector.rotate(self.rotation)
        rotate_with_speed = rotated_vec * PLAYER_SPEED * dt
        self.position += rotate_with_speed

    def shoot(self) -> None:
        if self.shot_timer <= 0:
            shot = Shot(self.position[0], self.position[1])
            shot.velocity = (
                pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOT_SPEED
            )
            self.shot_timer = PLAYER_SHOT_COOLDOWN_SECONDS

    def make_invincible(self):
        self.is_invincible = True
        self.invincible_timer = RESPAWN_INVINCIBLE_TIMER

    def update(self, dt: float) -> None:
        if self.is_invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.is_invincible = False
            phase = int(self.invincible_timer / RESPAWN_ANIMATION_INTERVAL)
            self.alpha = 255 if phase % 2 == 0 else 100
        self.shot_timer -= dt
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE] and not self.is_invincible:
            self.shoot()
