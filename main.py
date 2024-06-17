from mainmenu import *
from ursina import Ursina
from player import Player

class Main:
    def main():
        app = Ursina(title="MineClone", icon="res/icon.ico", borderless=False, editor_ui_enabled=False, development_mode=False)
        player = Player()
        menu = MainMenu(player=player, app=app)
        app.run()


    if __name__ == "__main__":
        main()
