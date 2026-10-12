import pygame
import pygame_gui

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from hud import Hud


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    hud_ui = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0.0
    hud = Hud(hud_ui)
    # hello_button = pygame_gui.elements.UIButton(
    #     relative_rect=pygame.Rect((350, 275), (100, 50)),
    #     text="Say Hello",
    #     manager=hud_ui,
    # )
    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            hud_ui.process_events(event)
        hud_ui.update(dt)
        screen.fill("black")
        hud_ui.draw_ui(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()
