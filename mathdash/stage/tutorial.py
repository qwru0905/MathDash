import json
from .base import *


class TutorialStage(Stage):
    BASE_PATH = "assets/tutorial/"

    def __init__(self):
        super().__init__()
        self.music = GameSound(f"{self.BASE_PATH}music.wav", loop=True)
        with open(f"{self.BASE_PATH}data.json", encoding="utf-8") as f:
            self.data = json.load(f)
        self._info = GameInfo.from_json(self.data)
        self.start_time = self.data.get("start_time", 0)
