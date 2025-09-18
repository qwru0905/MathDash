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


class Stage(ABC):
    result_map = {1: "자연수", 2: "정수", 3: "실수", 4: "허수"}

    def __init__(self, base_path: str):
        self.notes = [[] for _ in range(10)]
        self.now_note = [0] * 10
        self.now_additional_data = 0
        self.position = 0
        self.music_playing = False
        self.start_time = 0
        self.data: dict | None = None
        self.music: GameSound | None = None
        self._info: GameInfo | None = None
        self.input = Input()
        self.additional_data = []

        # decorations 관리
        self.decorations: list = []    # 모든 데코
        self.tag_map: dict[str, list] = {}  # 태그 → 데코들

        # JSON 로드
        import json
        with open(f"{base_path}data.json", encoding="utf-8") as f:
            self.data = json.load(f)

        settings = self.data.get("settings", {})
        self.music = GameSound(f"{base_path}{settings.get('file_name', 'music.wav')}", loop=True)
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

        font = pygame.font.SysFont("malgungothic", 30)

        for dec in self.data.get("decorations", []):
            if dec["type"] == "text":
                # 색상 hex → RGB
                hex_color = dec.get("color", "ffffff")
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

                surface = font.render(dec["text"], True, rgb).convert_alpha()
                surface.set_alpha(int(dec.get("opacity", 100) * 2.55))

                # 여러 태그 지원
                raw_tag = dec.get("tag", "")
                tags = raw_tag.split() if isinstance(raw_tag, str) else list(raw_tag)

                deco_obj = {
                    "tags": tags,
                    "surface": surface,
                    "pos": tuple(dec.get("pos", (0, 0))),
                    "rotation": dec.get("rotation", 0),
                    "scale": dec.get("scale", [100, 100]),
                    "depth": dec.get("depth", 0),
                    "opacity": dec.get("opacity", 100),
                    "text": dec["text"]
                }

                # 전체 리스트에 추가
                self.decorations.append(deco_obj)

                # 태그별 맵핑
                for tag in tags:
                    if tag not in self.tag_map:
                        self.tag_map[tag] = []
                    self.tag_map[tag].append(deco_obj)

            load_info.progress += 1

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
                self.notes[num].append(Note(num, equation, next_note_time, speed, 680, 820))

                note_index += 1
                next_note_time = self.data["notes"][note_index]["time"] \
                    if note_index < len(self.data["notes"]) else float('inf')
            else:
                # 액션 처리
                action_item = self.data["actions"][action_index]
                if action_item["type"] == "change_phase":
                    now_phase = action_item["phase"]
                else:
                    self.handle_action(action_item)

            action_index += 1
            next_action_time = self.data["actions"][action_index]["time"] \
                if action_index < len(self.data["actions"]) else float('inf')

            load_info.progress += 1

        load_info.complete = True

    def find_decorations_by_tag(self, tag: str):
        return self.tag_map.get(tag, [])

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

        # 장식 (depth 순서대로)
        for deco in sorted(self.decorations, key=lambda d: d["depth"]):
            surface = deco["surface"]
            x, y = deco["pos"]

            # 회전
            if deco["rotation"]:
                surface = pygame.transform.rotate(surface, deco["rotation"])
            # 스케일
            if deco["scale"] != [100, 100]:
                w, h = surface.get_size()
                surface = pygame.transform.smoothscale(
                    surface,
                    (int(w * deco["scale"][0] / 100), int(h * deco["scale"][1] / 100))
                )

            rect = surface.get_rect(center=(x, y))
            screen.blit(surface, rect)

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
    def handle_action(self, data: dict):
        pass
