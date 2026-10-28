import copy
import math
from itertools import combinations

import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_ACCELERATION,
    PLAYER_FRICTION,
    PLAYER_RADIUS,
    PLAYER_SHOT_COOLDOWN_SECONDS,
    PLAYER_SHOT_SPEED,
    PLAYER_TURN_SPEED,
    RESPAWN_ANIMATION_INTERVAL,
    RESPAWN_INVINCIBLE_TIMER,
    SHOT_RADIUS,
)
from polygonshape import LineSegment, PolygonShape
from shot import Shot


class Player(PolygonShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_timer = 0
        self.is_invincible = False
        self.alpha = 255
        self.line_list = list(
            map(lambda x: LineSegment(x[0], x[1]), combinations(self.triangle(), 2))
        )
        self.speed = pygame.Vector2(0, 0)
        # print(self.line_list)

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def clone_triangle(self) -> list[pygame.Vector2] | None:
        if not self.clone_pos:
            return None
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.clone_pos + forward * self.radius
        b = self.clone_pos - forward * self.radius - right
        c = self.clone_pos - forward * self.radius + right
        return [a, b, c]

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
        pygame.draw.polygon(
            shape_surf,
            (255, 255, 255, int(self.alpha)),
            [(x - min_x, y - min_y) for x, y in self.triangle()],
            # self.triangle(),
            LINE_WIDTH,
        )
        screen.blit(shape_surf, target_rect)
        self.clone_draw(screen)

    def clone_draw(self, screen) -> None:
        if not self.clone_pos:
            return
        lx, ly = zip(*self.clone_triangle())
        min_x, min_y, max_x, max_y = (
            min(lx) - LINE_WIDTH,
            min(ly) - LINE_WIDTH,
            max(lx) + LINE_WIDTH,
            max(ly) + LINE_WIDTH,
        )
        target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(
            shape_surf,
            (255, 255, 255, int(self.alpha)),
            [(x - min_x, y - min_y) for x, y in self.clone_triangle()],
            # self.triangle(),
            LINE_WIDTH,
        )
        screen.blit(shape_surf, target_rect)

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt: float) -> None:
        unit_vector = pygame.Vector2(0, 1)
        rotated_vec = unit_vector.rotate(self.rotation)
        self.speed = rotated_vec * PLAYER_ACCELERATION * dt + self.speed
        self.speed = self.speed * PLAYER_FRICTION
        self.position += self.speed
        self.line_list = list(
            map(lambda x: LineSegment(x[0], x[1]), combinations(self.triangle(), 2))
        )
        if self.clone_pos:
            self.line_list.extend(
                list(
                    map(
                        lambda x: LineSegment(x[0], x[1]),
                        combinations(self.clone_triangle(), 2),
                    )
                )
            )

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
        self.wrap_around()

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
        if not keys[pygame.K_w] and not keys[pygame.K_s]:
            self.move(0)
