import json
from pathlib import Path

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIWindow


class LeaderboardUI:
    def __init__(self, ui: pygame_gui.UIManager) -> None:
        self.ui_manager = ui
        new_score_rect = pygame.Rect(31, 38, 420, 644)
        self.new_score_container = UIPanel(new_score_rect, manager=ui, visible=True)
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-70, -60, 130, 30),
            text="exit game",
            manager=ui,
            visible=True,
            container=self.new_score_container,
            anchors={
                "centerx": "centerx",
                "bottom": "bottom",
                # "right": "right",
                # "top": "top",
                # "bottom": "bottom",
            },
        )
        self.new_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(70, -60, 130, 30),
            text="new game",
            manager=ui,
            visible=True,
            container=self.new_score_container,
            anchors={
                "centerx": "centerx",
                "bottom": "bottom",
            },
        )
        self.highscore_message = pygame_gui.elements.UILabel(
            text="New High Score!",
            relative_rect=pygame.Rect(0, 30, -1, 40),
            manager=ui,
            container=self.new_score_container,
            anchors={"centerx": "centerx", "top": "top"},
        )
        self.run_score = pygame_gui.elements.UILabel(
            text="Score placeholder",
            relative_rect=pygame.Rect(0, 60, -1, 40),
            manager=ui,
            container=self.new_score_container,
            anchors={"centerx": "centerx", "top": "top"},
        )
        self.rank_num = pygame_gui.elements.UILabel(
            text="Rank placeholder",
            relative_rect=pygame.Rect(0, -60, -1, 80),
            manager=ui,
            container=self.new_score_container,
            anchors={"centerx": "centerx", "centery": "centery"},
        )
        self.name_entry = pygame_gui.elements.UITextEntryBox(
            initial_text="Enter your name here",
            relative_rect=pygame.Rect(-70, 90, 180, 40),
            manager=ui,
            container=self.new_score_container,
            anchors={"centerx": "centerx", "centery": "centery"},
        )
        self.submit_score_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(90, 90, 80, 30),
            text="submit",
            manager=ui,
            visible=True,
            container=self.new_score_container,
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
        )

        high_scores_rect = pygame.Rect(480, 38, 750, 644)
        self.high_scores_container = UIPanel(high_scores_rect, manager=ui, visible=True)

        self.high_scores_text = pygame_gui.elements.UILabel(
            text="High Scores",
            relative_rect=pygame.Rect(0, 25, -1, 80),
            manager=ui,
            container=self.high_scores_container,
            anchors={"centerx": "centerx", "top": "top"},
        )

    def set_visible(self) -> None:
        self.exit_button.visible = True
        self.new_score_container.visible = True

    def set_player_score(self, current_score: int, player_rank: int) -> None:
        self.run_score.set_text("Score: " + str(current_score))
        self.rank_num.set_text("Rank: " + str(player_rank))

    def create_score_ui_entries(self, scores: list[tuple[str, int]]):
        text_dy = 20
        text_x = 150
        text_y = 50
        self.rank_text = pygame_gui.elements.UILabel(
            text="Rank",
            relative_rect=pygame.Rect(text_x, text_y, -1, 80),
            manager=self.ui_manager,
            container=self.high_scores_container,
            anchors={"left": "left", "top": "top"},
        )
        self.name_text = pygame_gui.elements.UILabel(
            text="Name",
            relative_rect=pygame.Rect(0, text_y, -1, 80),
            manager=self.ui_manager,
            container=self.high_scores_container,
            anchors={"centerx": "centerx", "top": "top"},
        )
        self.score_text = pygame_gui.elements.UILabel(
            text="Score",
            relative_rect=pygame.Rect(-text_x, text_y, -1, 80),
            manager=self.ui_manager,
            container=self.high_scores_container,
            anchors={"right": "right", "top": "top"},
        )
        for i in range(0, len(scores)):
            text_y += text_dy
            pygame_gui.elements.UILabel(
                text=str(i + 1),
                relative_rect=pygame.Rect(text_x, text_y, -1, 80),
                manager=self.ui_manager,
                container=self.high_scores_container,
                anchors={"left": "left", "top": "top"},
            )
            pygame_gui.elements.UILabel(
                text=scores[i][0],
                relative_rect=pygame.Rect(0, text_y, -1, 80),
                manager=self.ui_manager,
                container=self.high_scores_container,
                anchors={"centerx": "centerx", "top": "top"},
            )
            pygame_gui.elements.UILabel(
                text=str(scores[i][1]),
                relative_rect=pygame.Rect(-text_x, text_y, -1, 80),
                manager=self.ui_manager,
                container=self.high_scores_container,
                anchors={"right": "right", "top": "top"},
            )


class Leaderboard:
    def __init__(self, path: Path, ui: pygame_gui.UIManager) -> None:
        self.path = path
        if not self.path.exists():
            if not self.path.parent.exists():
                self.path.parent.mkdir()
            self.path.touch()

        self.content = self.__read_leaderboard()
        self.gui = LeaderboardUI(ui)
        self.gui.create_score_ui_entries(self.content)

    def __read_leaderboard(self) -> list[tuple[str, int]]:
        def create_empty_entries(
            scores: list[tuple[str, int]],
        ) -> list[tuple[str, int]]:
            scores.extend([("No score yet", 0)] * (10 - len(scores)))
            return scores

        with open(self.path, "r") as f:
            try:
                scores = json.load(f)
            except json.decoder.JSONDecodeError:
                return create_empty_entries([])
            scores = [tuple(score) for score in scores]
            if len(scores) < 10:
                scores = create_empty_entries(scores)
            return scores

    # Append score
    def add_score(self, score: int) -> int:
        new_score = (self.gui.name_entry.get_text(), score)
        for i, entry in enumerate(self.content):
            if new_score[1] >= entry[1]:
                # Replace, push rest down
                self.content.insert(i, new_score)
                self.content = self.content[:10]
                return i + 1
        return 0

    def write_file(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self.content, f)
