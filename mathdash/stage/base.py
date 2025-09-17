import random

import pygame

from mathdash.core.note import Note
from mathdash.core.sound import GameSound
from dataclasses import dataclass
from abc import ABC, abstractmethod
from mathdash.core.input import Input


@dataclass(frozen=True)
class GameInfo:
    name: str
    description: str
    gimmick: str
    difficult: int

    @classmethod
    def from_json(cls, data: dict) -> "GameInfo":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            gimmick=data.get("gimmick", ""),
            difficult=data.get("difficult", 0),
        )


@dataclass
class LoadInfo:
    description: str = ""
    progress: int = 0
    max_progress: int = 0
    complete: bool = False


class Stage(ABC):
    result_map = {1: "자연수", 2: "정수", 3: "실수", 4: "허수"}

    def __init__(self):
        self.notes = [[], [], [], [], [], [], [], [], [], []]
        self.now_note = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.now_additional_data = 0
        self.position = 0
        self.music_playing = False
        self.start_time = 0
        self.data: dict | None = None
        self.music: GameSound | None = None
        self._info: GameInfo | None = None
        self.input = Input()
        self.additional_data = []

    @property
    def info(self) -> GameInfo:
        return self._info

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
                self.notes[num].append(Note(num, equation, next_note_time, speed, 680, 820))

                note_index += 1
                next_note_time = self.data["notes"][note_index]["time"] \
                    if note_index < len(self.data["notes"]) else float('inf')
            else:
                # 데이터 처리
                data_item = self.data["data"][data_index]
                if data_item["type"] == "change_phase":
                    now_phase = data_item["phase"]
                else:
                    self.additional_data.append(data_item)

                data_index += 1
                next_data_time = self.data["data"][data_index]["time"] \
                    if data_index < len(self.data["data"]) else float('inf')

            load_info.progress += 1

        load_info.complete = True

    def start(self):
        if self.start_time >= 0:
            self.music.play()
            self.music.position = int(self.start_time)
            self.music_playing = True
        self.position = self.start_time

    def update(self, delta_time):
        if self.start_time < 0 and not self.music_playing:
            if self.position < 0:
                self.position += delta_time * 1000
            else:
                self.music.play()
                self.music.position = int(self.position)
                self.music_playing = True

        if self.music_playing:
            self.position = self.music.position

        if self.now_additional_data < len(self.additional_data):
            self.handle_additional_data(self.additional_data[self.now_additional_data])
            self.now_additional_data += 1

        for line_idx, note_line in enumerate(self.notes):
            for note in note_line[self.now_note[line_idx]:]:
                result = note.update(self.position)
                if result == -1:  # 노트 처리 완료
                    self.now_note[line_idx] += 1

        for btn_idx, btn in enumerate(self.input.buttons):
            if btn.changed and btn.is_down:
                if btn_idx < len(self.notes) and self.now_note[btn_idx] < len(self.notes[btn_idx]):
                    result = self.notes[btn_idx][self.now_note[btn_idx]].judge(self.position)
                    if result != 0:
                        self.now_note[btn_idx] += 1
                else:
                    result = 0
                print(self.result_map.get(result, "너 뭐함"))

    def draw(self, screen):
        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (0, 0, 0), (680, 688), 40)

        for line_idx, note_line in enumerate(self.notes):
            note_idx = self.now_note[line_idx]
            if note_idx >= len(note_line):
                continue

            for note in note_line[note_idx:]:
                note.draw(screen)

    def event(self, events):
        for btn in self.input.buttons:
            btn.changed = False

        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                is_down = event.type == pygame.KEYDOWN
                vk_code = event.key

                key_to_num = {
                    pygame.K_0: 0, pygame.K_KP0: 0,
                    pygame.K_1: 1, pygame.K_KP1: 1,
                    pygame.K_2: 2, pygame.K_KP2: 2,
                    pygame.K_3: 3, pygame.K_KP3: 3,
                    pygame.K_4: 4, pygame.K_KP4: 4,
                    pygame.K_5: 5, pygame.K_KP5: 5,
                    pygame.K_6: 6, pygame.K_KP6: 6,
                    pygame.K_7: 7, pygame.K_KP7: 7,
                    pygame.K_8: 8, pygame.K_KP8: 8,
                    pygame.K_9: 9, pygame.K_KP9: 9,
                }

                if vk_code in key_to_num:
                    b = key_to_num[vk_code]
                    self.input.buttons[b].changed = \
                        (is_down != self.input.buttons[b].is_down)
                    self.input.buttons[b].is_down = is_down

    @abstractmethod
    def handle_additional_data(self, data: dict):
        pass
