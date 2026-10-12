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
        self.name_entry = pygame_gui.elements.UITextEntryLine(
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

        self.high_scores_rect = pygame.Rect(480, 38, 750, 644)
        self.high_scores_container = UIPanel(
            self.high_scores_rect, manager=ui, visible=True
        )

    def set_visible(self, show_both: bool) -> None:
        self.ui_manager.root_container.show()
        self.name_entry.set_text("Enter your name here")
        self.name_entry.enable()
        self.submit_score_button.enable()
        if show_both:
            self.name_entry.focus()
        if not show_both:
            self.new_score_container.hide()

    def set_player_score(self, current_score: int, player_rank: int) -> None:
        self.run_score.set_text("Score: " + str(current_score))
        self.rank_num.set_text("Rank: " + str(player_rank))

    def reload_scores(self, scores: list[tuple[str, int]]):
        self.high_scores_container.kill()
        self.high_scores_container = UIPanel(
            self.high_scores_rect, manager=self.ui_manager, visible=True
        )
        self.create_score_ui_entries(scores)

    def create_score_ui_entries(self, scores: list[tuple[str, int]]):
        text_dy = 20
        text_x = 150
        text_y = 50
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-70, -60, 130, 30),
            text="exit game",
            manager=self.ui_manager,
            visible=True,
            container=self.high_scores_container,
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
            manager=self.ui_manager,
            visible=True,
            container=self.high_scores_container,
            anchors={
                "centerx": "centerx",
                "bottom": "bottom",
            },
        )
        self.high_scores_text = pygame_gui.elements.UILabel(
            text="High Scores",
            relative_rect=pygame.Rect(0, 25, -1, 80),
            manager=self.ui_manager,
            container=self.high_scores_container,
            anchors={"centerx": "centerx", "top": "top"},
        )
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
        self.player_rank = 0
        self.player_score = 0

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

    def submit_score(self) -> None:
        self.write_score()
        self.write_file()
        self.gui.name_entry.disable()
        self.gui.submit_score_button.disable()
        self.gui.reload_scores(self.content)

    # Append score
    def add_score(self, score: int) -> None:
        self.player_score = score
        new_score = (self.gui.name_entry.get_text(), score)
        for i, entry in enumerate(self.content):
            if new_score[1] >= entry[1]:
                # Replace, push rest down
                self.player_rank = i + 1
                return
        self.player_rank = 0

    def write_score(self) -> None:
        self.content.insert(
            self.player_rank - 1, (self.gui.name_entry.get_text(), self.player_score)
        )
        self.content = self.content[:10]

    def write_file(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self.content, f)
