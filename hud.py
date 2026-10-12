import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIPanel

from constants import INITIAL_LIVES


class Hud:
    def __init__(self, ui: pygame_gui.UIManager) -> None:
        self.ui_manager = ui
        self.score_container = UIPanel(
            pygame.Rect(-150, 60, -1, 80), manager=ui, visible=True
        )
        self.score_counter = UILabel(
            text="Score: 0",
            relative_rect=pygame.Rect(-110, 20, 100, 50),
            manager=ui,
            # container=self.score_container,
            anchors={"right": "right", "top": "top"},
        )
        self.lives_counter = UILabel(
            text=f"Lives: {INITIAL_LIVES}",
            relative_rect=pygame.Rect(-110, 40, 100, 50),
            manager=ui,
            anchors={"right": "right", "top": "top"},
        )

    def update_score(self, score: int) -> None:
        self.score_counter.set_text("Score: " + str(score))

    def update_lives(self, num: int) -> None:
        self.lives_counter.set_text("Lives: " + str(num))
