from ursina import Ursina, Sky
from player import Player
from mob import Mob
from mainmenu import MainMenu

class Main:
    @staticmethod
    def main():
        app = Ursina(
            title="MineClone",
            icon="res/icon.ico",
            borderless=False,
            editor_ui_enabled=False,
            development_mode=False,
            auto_aspect_ratio=True,  # Automatically adjust aspect ratio based on window size
            size=(1280, 720),
            fullscreen=False,
            exit_button=True,  # Show exit button in the window
            resizable=True,  # Allow the window to be resizable
            show_ursina_splash=False,  # Disable Ursina splash screen
            quality_level=0,  # Set quality level (0 - low, 3 - high)
            max_entities_in_view=1000,  # Adjust based on performance needs
            anti_aliasing=True  # Enable anti-aliasing
        )

        # Customize sky (for now we'll leave it as is, if you wanna change the texture
        # just add the texture= argument to Sky())
        sky = Sky()
        app.sky = sky

        # Create player and initialize game components
        player = Player()
        menu = MainMenu(player, app)

        # Spawn mobs
        Mob.spawn_continuous_mobs(player)

        app.run()

if __name__ == "__main__":
    Main.main()
