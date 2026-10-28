import pygame

from constants import LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.clone_pos: "None | pygame.Vector2" = None
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        # must override
        pass

    def update(self, dt: float) -> None:
        # must override
        pass

    def wrap_around(self) -> None:
        clone_pos = self.position.copy()
        rad = self.radius + LINE_WIDTH
        if self.position[0] + rad >= SCREEN_WIDTH:
            clone_pos[0] -= SCREEN_WIDTH
        elif self.position[0] - rad <= 0:
            clone_pos[0] += SCREEN_WIDTH
        if self.position[1] + rad >= SCREEN_HEIGHT:
            clone_pos[1] -= SCREEN_HEIGHT
        elif self.position[1] - rad <= 0:
            clone_pos[1] += SCREEN_HEIGHT

        if (
            self.position[0] - rad >= SCREEN_WIDTH
            or self.position[0] + rad <= 0
            or self.position[1] - rad >= SCREEN_HEIGHT
            or self.position[1] + rad <= 0
        ):
            self.position = clone_pos
            self.clone_pos = None

        if clone_pos != self.position:
            self.clone_pos = clone_pos
        else:
            self.clone_pos = None

    def collides_with(self, other: "CircleShape") -> bool:
        if self.position.distance_to(other.position) < self.radius + other.radius:
            return True
        elif (
            self.clone_pos
            and self.clone_pos.distance_to(other.position) < self.radius + other.radius
        ):
            return True
        return False
