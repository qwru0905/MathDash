from .base import *


class TutorialStage(Stage):
    BASE_PATH = "assets/tutorial/"

    def __init__(self):
        super().__init__(self.BASE_PATH)  # Stage에 BASE_PATH 전달

    def handle_action(self, data: dict):
        # 추가 데이터
        pass



