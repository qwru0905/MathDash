import os
from tkinter import filedialog

from .base import *


class CustomStage(Stage):
    def __init__(self):
        file_path = None
        while not file_path:
            file_path = filedialog.askopenfilename(
                title="파일 선택",
                filetypes=(("json 파일", "*.json"), ("모든 파일", "*.*"))
            )

        base_path = os.path.dirname(file_path)
        super().__init__(base_path)  # Stage에 BASE_PATH 전달

    def handle_action(self, data: dict):
        # 추가 데이터
        pass



