import pathlib
import sys

import pygame
import pygame_gui

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from hud import Hud
from logger import log_event, log_state
from player import Player
from score import Leaderboard
from shot import Shot


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    ui = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    hud_ui = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
    ui.root_container.hide()
    hud_ui.root_container.show()
    clock = pygame.time.Clock()
    dt = 0.0
    score = 0
    lives = 3
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
    hud = Hud(hud_ui)

    # Main game loop
    while True:
        log_state()
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            hud_ui.process_events(event)
            ui.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == leaderboard.gui.exit_button:
                    return
                if event.ui_element == leaderboard.gui.new_game_button:
                    asteroid_field = AsteroidField()
                    main_player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    leaderboard.gui.ui_manager.root_container.hide()
                    score = 0
                    player_rank = 0
                if event.ui_element == leaderboard.gui.submit_score_button:
                    leaderboard.submit_score()
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if "Enter your name here" in leaderboard.gui.name_entry.get_text():
                    leaderboard.gui.name_entry.set_text(
                        leaderboard.gui.name_entry.get_text()
                        .removesuffix("Enter your name here")
                        .removeprefix("Enter your name here")
                    )
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                leaderboard.submit_score()

        screen.fill("black")
        ui.update(dt)
        hud_ui.update(dt)
        updatable.update(dt)
        for asteroid in asteroids:
            if asteroid.collides_with(main_player) and not main_player.is_invincible:
                log_event("player_hit")
                # print("Game over!")
                if lives > 1:
                    main_player.position = pygame.Vector2(
                        SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
                    )
                    lives -= 1
                    hud.update_lives(lives)
                    main_player.make_invincible()
                else:
                    for asteroid in asteroids:
                        asteroid.kill()
                    main_player.kill()
                    asteroid_field.kill()
                    leaderboard.add_score(score)
                    if leaderboard.player_rank != 0:
                        leaderboard.gui.set_player_score(score, leaderboard.player_rank)
                        leaderboard.gui.set_visible(True)
                    else:
                        leaderboard.gui.set_visible(False)
                    hud.ui_manager.root_container.hide()
            for shot in shots:
                if asteroid.collides_with(shot):
                    score += 1
                    hud.update_score(score)
                    log_event("asteroid_shot")
                    asteroid.split()
                    shot.kill()
        ui.draw_ui(screen)
        hud_ui.draw_ui(screen)
        for player in drawable:
            player.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
