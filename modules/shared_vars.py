import os

class SharedVariables:
    def __init__(self):
        self.GAME_FOLDER = None
        self.BEPINEX_FOLDER = None
        self.PLUGINS_FOLDER = None
        self.TEMP_FOLDER = "temp"
    def set_game_path(self, path):
        self.GAME_FOLDER = path
        self.BEPINEX_FOLDER = os.path.join(self.GAME_FOLDER, "BepInEx")
        self.PLUGINS_FOLDER = os.path.join(self.BEPINEX_FOLDER, "plugins")

shared_vars = SharedVariables()