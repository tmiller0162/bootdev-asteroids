import pygame

from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_RADIUS,
    PLAYER_SHOT_COOLDOWN_SECONDS,
    PLAYER_SHOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    SHOT_RADIUS,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_timer = 0

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen) -> None:
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

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

    def update(self, dt: float) -> None:
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
        if keys[pygame.K_SPACE]:
            self.shoot()
