import json
from mathdash.sound import GameSound
from .stage import *
from mathdash.note import Note
import random


class TutorialStage(Stage):
    BASE_PATH = "assets/tutorial/"

    def __init__(self):
        super().__init__()
        self.music = GameSound(f"{self.BASE_PATH}music.wav", loop=True)
        with open(f"{self.BASE_PATH}data.json", encoding="utf-8") as f:
            self.data = json.load(f)
        self._info = GameInfo.from_json(self.data)
        self.notes = []
        self.additional_data = []

    def load(self, load_info: LoadInfo):
        load_info.description = "노트 & 데이터"
        load_info.progress = 0
        load_info.max_progress = len(self.data["notes"]) + len(self.data["data"])

        note_index = 0
        data_index = 0
        now_phase = 0
        speed = self.data["speed"]

        # 초기 시간 설정
        next_note_time = self.data["notes"][note_index]["time"] if self.data["notes"] else float('inf')
        next_data_time = self.data["data"][data_index]["time"] if self.data["data"] else float('inf')

        while load_info.progress < load_info.max_progress:
            if next_note_time <= next_data_time:
                # 노트 처리
                num = self.data["notes"][note_index]["num"]
                equation_len = len(self.data["equation"][now_phase][num])
                equation = self.data["equation"][now_phase][num][random.randrange(equation_len)]
                self.notes.append(Note(num, equation, next_note_time, speed, 680, 820))

                note_index += 1
                next_note_time = self.data["notes"][note_index]["time"]\
                    if note_index < len(self.data["notes"]) else float('inf')
            else:
                # 데이터 처리
                data_item = self.data["data"][data_index]
                if data_item["type"] == "change_phase":
                    now_phase = data_item["phase"]
                else:
                    self.additional_data.append(data_item)

                data_index += 1
                next_data_time = self.data["data"][data_index]["time"]\
                    if data_index < len(self.data["data"]) else float('inf')

            load_info.progress += 1

        load_info.complete = True
