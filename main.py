import pathlib
import sys

import pygame
import pygame_gui

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event, log_state
from player import Player
from score import Leaderboard
from shot import Shot


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    ui = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0.0
    score = 0
    player_rank = 0
    leader_path = pathlib.Path("./save_data/leaderboard.json")

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)

    main_player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()
    # print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    # print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")
    leaderboard = Leaderboard(leader_path, ui)

    # Main game loop
    while True:
        log_state()
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            ui.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == leaderboard.gui.exit_button:
                    return
                if event.ui_element == leaderboard.gui.new_game_button:
                    raise NotImplementedError
                if event.ui_element == leaderboard.gui.submit_score_button:
                    leaderboard.write_file()
                    leaderboard.gui.name_entry.visible = False
                    leaderboard.gui.submit_score_button.visible = False
        screen.fill("black")
        # main_player.update(dt)
        ui.update(dt)
        updatable.update(dt)
        for asteroid in asteroids:
            if asteroid.collides_with(main_player):
                # leaderboard.add_score(score)
                # leaderboard.write_file()
                # TODO ask for name, display leaderboard
                log_event("player_hit")
                print("Game over!")
                for asteroid in asteroids:
                    asteroid.kill()
                main_player.kill()
                asteroid_field.kill()
                player_rank = leaderboard.add_score(score)
                leaderboard.gui.set_player_score(score, player_rank)

                leaderboard.gui.set_visible()
                # sys.exit()
            for shot in shots:
                if asteroid.collides_with(shot):
                    score += 1
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()
        ui.draw_ui(screen)
        for player in drawable:
            player.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
