from ursina import Button
from ursina import color
from ursina import application
from utils import Utils

class MainMenu():
    def __init__(self, player, app):
        self.player = player
        self.app = app
        player.enabled = False
        # Create menu buttons with correct function assignments
        self.start_button = Button(
            text='Start Game',
            color=color.azure,
            scale=(0.2, 0.1),
            position=(0, 0.1),
            on_click=self.start_game  # Assign start_game function itself
        )
        self.quit_button = Button(
            text='Quit',
            color=color.azure,
            scale=(0.2, 0.1),
            position=(0, 0.0),
            on_click=application.quit
        )

    def start_game(self):
        for box in self.player.boxes:
            box.enabled = True
        self.player.enabled = True
        self.start_button.enabled = False
        self.quit_button.enabled = False