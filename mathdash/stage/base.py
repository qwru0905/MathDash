import os
from dataclasses import dataclass

import json
import random

import pygame
from abc import ABC, abstractmethod

from mathdash.core.sound import GameSound
from mathdash.core.input import Input
from mathdash.managers import *


# ====== 데이터 클래스 ======
@dataclass(frozen=True)
class GameInfo:
    name: str
    description: str
    gimmick: str
    difficult: int

    @classmethod
    def from_json(cls, data: dict) -> "GameInfo":
        settings = data.get("settings", {})
        return cls(
            name=settings.get("name", ""),
            description=settings.get("description", ""),
            gimmick=settings.get("gimmick", settings.get("gimmik", "")),  # 오타 대응
            difficult=settings.get("difficult", 0),
        )


@dataclass
class LoadInfo:
    description: str = ""
    progress: int = 0
    max_progress: int = 0
    complete: bool = False


# ====== Stage 클래스 ======
class Stage(ABC):
    result_map = {1: "자연수", 2: "정수", 3: "실수", 4: "허수"}

    def __init__(self, base_path: str):
        self.now_additional_data = 0
        self.position = 0
        self.music_playing = False
        self.start_time = 0
        self.data: dict | None = None
        self.music: GameSound | None = None
        self._info: GameInfo | None = None
        self.input = Input()

        # managers
        self.note_manager = NoteManager()
        self.dec_manager = DecorationManager(base_path)
        self.act_manager = ActionManager()

        # JSON 로드
        with open(os.path.join(base_path, "data.json"), encoding="utf-8") as f:
            self.data = json.load(f)

        settings = self.data.get("settings", {})
        self.music = GameSound(os.path.join(base_path, settings.get('file_name', 'music.wav')), loop=False)
        self._info = GameInfo.from_json(self.data)
        self.start_time = settings.get("start_time", 0)

    @property
    def info(self) -> GameInfo:
        return self._info

    def load(self, load_info: LoadInfo):
        # Decorations 먼저 로드
        load_info.description = "장식"
        load_info.progress = 0
        load_info.max_progress = len(self.data.get("decorations", []))

        font = pygame.font.SysFont("malgungothic", 30)

        self.dec_manager.load_from_json(self.data.get("decorations", []), font, load_info)

        load_info.description = "노트 & 액션"
        load_info.progress = 0
        load_info.max_progress = len(self.data.get("notes", [])) + len(self.data.get("actions", []))

        note_index = 0
        action_index = 0
        now_phase = 0
        speed = self.data["settings"].get("speed", 5)

        next_note_time = self.data["notes"][note_index]["time"] if self.data.get("notes") else float('inf')
        next_action_time = self.data["actions"][action_index]["time"] if self.data.get("actions") else float('inf')

        while load_info.progress < load_info.max_progress:
            if next_note_time <= next_action_time:
                # 노트 처리
                num = self.data["notes"][note_index]["num"]
                equation_len = len(self.data["equation"][now_phase][num])
                equation = self.data["equation"][now_phase][num][random.randrange(equation_len)]

                self.note_manager.add_note(
                    num, equation, next_note_time, speed, 680, 820
                )

                note_index += 1
                next_note_time = self.data["notes"][note_index]["time"] \
                    if note_index < len(self.data["notes"]) else float('inf')
            else:
                # 액션 처리
                action_item = self.data["actions"][action_index]
                if action_item["type"] == "change_phase":
                    now_phase = action_item["phase"]
                elif action_item["type"] in ["move_decorations"]:
                    self.act_manager.add_action(action_item)
                else:
                    self.handle_action(action_item)

            action_index += 1
            next_action_time = self.data["actions"][action_index]["time"] \
                if action_index < len(self.data["actions"]) else float('inf')

            load_info.progress += 1

        load_info.complete = True

    def start(self):
        if self.start_time >= 0:
            self.music.play()
            self.music.position = int(self.start_time)
            self.music_playing = True
        self.position = self.start_time

    def update(self, delta_time):
        # ====== 음악 position 갱신 ======
        if self.start_time < 0 and not self.music_playing:
            if self.position < 0:
                self.position += delta_time * 1000
            else:
                self.music.play()
                self.music.position = int(self.position)
                self.music_playing = True

        if self.music_playing:
            self.position = self.music.position

        now = self.position

        self.act_manager.update(now, self.dec_manager.find_by_tags)
        self.note_manager.update(now)

        # ====== 입력 처리 ======
        for btn_idx, btn in enumerate(self.input.buttons):
            if btn.changed and btn.is_down:
                result = self.note_manager.judge(btn_idx, now)
                print(self.result_map.get(result, "너 뭐함"))

    # 장식 (depth 순서대로)
    def draw(self, screen):
        screen.fill((30, 30, 30))

        self.dec_manager.draw(screen, before=False)

        pygame.draw.circle(screen, (255, 255, 255), (680, 688), 40, 2)
        pygame.draw.circle(screen, (0, 0, 0), (680, 688), 38)

        self.note_manager.draw(screen)

        self.dec_manager.draw(screen, before=True)

    def event(self, events):
        for btn in self.input.buttons:
            btn.changed = False

        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                is_down = event.type == pygame.KEYDOWN
                vk_code = event.key

                if vk_code in KEY_TO_NUM:
                    b = KEY_TO_NUM[vk_code]
                    self.input.buttons[b].changed = \
                        (is_down != self.input.buttons[b].is_down)
                    self.input.buttons[b].is_down = is_down

    @abstractmethod
    def handle_action(self, data: dict):
        pass
