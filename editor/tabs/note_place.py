import copy
import json
import os

import pygame

from mathdash.core.sound import GameSound
from .tab import Tab


class NullSound:
    """아무 소리도, 아무 동작도 하지 않는 가짜 GameSound 객체."""
    def __init__(self):
        self._position = 0

    # ----------------------
    # 재생 관련
    # ----------------------
    def play(self) -> None:
        """사운드 재생"""
        pass

    @property
    def paused(self) -> bool | None:
        return True

    @paused.setter
    def paused(self, paused: bool) -> None:
        pass

    def stop(self) -> None:
        pass

    # ----------------------
    # 볼륨 관련
    # ----------------------
    def _apply_volume(self) -> None:
        """현재 볼륨을 채널에 반영"""
        pass

    def set_volume(self, value: float) -> None:
        """볼륨을 직접 설정"""
        pass

    def volume_up(self) -> None:
        """볼륨 증가"""
        pass

    def volume_down(self) -> None:
        """볼륨 감소"""
        pass

    # ----------------------
    # 위치 관련
    # ----------------------
    @property
    def position(self) -> int:
        """현재 재생 위치(ms). 채널이 없으면 -1 반환"""
        return self._position

    @position.setter
    def position(self, position: int) -> None:
        """재생 위치를 ms 단위로 이동"""
        self._position = position


myFont = pygame.font.SysFont("arial", 30, True, False)

# 클래스 상단에 상수 정의
LANE_WIDTH = 50
LANE_OFFSET = 25
NOTE_SPEED = 0.2  # 시간에 따른 y 좌표 스케일
NOTE_RADIUS = 25
SCROLL_SPEED_KEYBOARD = 300
SCROLL_SPEED_MOUSE = 100
NOTE_CENTER_Y = 600


class NotePlace(Tab):
    def __init__(self):
        self.base_path = None
        self.data: dict | None = None
        self.music: GameSound = NullSound()
        self.notes: list[dict] = []
        self.bpm_changes: list[dict] = [
            {"time": 0, "bpm": 120, "time_signature": (4, 4)}
        ]
        self.beat_unit = 4  # 임시

    def open_file(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            self.data = json.load(f)

        self.base_path = os.path.dirname(file_path)
        settings = self.data.get("settings", {})
        music_file = settings.get('file_name', 'music.wav')
        music_path = os.path.join(self.base_path, music_file)
        self.music = GameSound(music_path, loop=False)
        self.music.play()
        self.music.paused = True
        self.notes = self.data.get("notes", {})
        self.bpm_changes = self.data.get("bpm", [])  # 변속도 정보 저장

    def update(self):
        pass

    def get_current_bpm(self, position_ms: int) -> dict:
        """현재 위치에 적용되는 bpm/time_signature 반환"""
        current = copy.deepcopy(self.bpm_changes[0]) if self.bpm_changes else {"time": 0, "bpm": 120, "time_signature": (4, 4)}
        for change in self.bpm_changes:
            if position_ms >= change["time"]:
                current["time"] = change["time"]
                current["bpm"] = change["bpm"]
                if "time_signature" in change:
                    current["time_signature"] = tuple(change["time_signature"])
            else:
                break
        return current

    def event(self, events):
        for e in events:
            # 화살표 위/아래
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.music.position -= SCROLL_SPEED_KEYBOARD
                elif e.key == pygame.K_DOWN:
                    self.music.position += SCROLL_SPEED_KEYBOARD
                elif e.key == pygame.K_SPACE:
                    self.music.paused = not self.music.paused
                elif e.key == pygame.K_d:
                    print(self.bpm_changes)

            # 마우스 휠
            elif e.type == pygame.MOUSEWHEEL:
                self.music.position -= e.y * SCROLL_SPEED_MOUSE  # y>0이면 위로, y<0이면 아래로

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:  # 왼쪽 클릭
                    x, y = e.pos
                    y -= 30  # 메뉴바 높이 보정

                    if LANE_OFFSET < x < LANE_OFFSET + LANE_WIDTH * 10 and 0 < y < 1200:
                        lane_num = (x - LANE_OFFSET) // LANE_WIDTH

                        # 클릭한 위치의 절대 시간
                        note_time = self.music.position + (NOTE_CENTER_Y - y) / NOTE_SPEED

                        # note_time 기준으로 bpm 구하기
                        bpm_info = self.get_current_bpm(note_time)
                        bpm = bpm_info["bpm"]
                        numer, denom = bpm_info["time_signature"]

                        measure_interval = (60000 / bpm) * (4 / denom) * numer
                        beat_interval = (60000 / bpm) * (4 / self.beat_unit)

                        real_note_time = 0
                        current_measure_time = bpm_info["time"]
                        while current_measure_time <= note_time + beat_interval:
                            # 박자 단위 선
                            t = current_measure_time
                            while t < current_measure_time + measure_interval:
                                real_note_time = t \
                                    if abs(t - note_time) < abs(real_note_time - note_time) else real_note_time
                                t += beat_interval

                            current_measure_time += measure_interval

                        self.notes.append({
                            "num": int(lane_num),
                            "time": int(real_note_time)
                        })

                elif e.button == 3:  # 오른쪽 클릭
                    x, y = e.pos
                    if LANE_OFFSET < x < LANE_OFFSET + LANE_WIDTH * 10 and 0 < y < 1200:
                        lane_num = (x - LANE_OFFSET) // LANE_WIDTH
                        note_time = self.music.position + (NOTE_CENTER_Y - y) / NOTE_SPEED
                        # 가장 가까운 노트 찾기
                        closest_note = None
                        closest_dist = float('inf')
                        for note in self.notes:
                            if note["num"] == int(lane_num):
                                dist = abs(note["time"] - note_time)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_note = note
                        # 일정 거리 이내면 삭제
                        if closest_note and closest_dist < 500:  # 500ms 이내
                            self.notes.remove(closest_note)

    def draw(self, surface: pygame.Surface):
        surface.fill((0, 0, 0))
        width, height = surface.get_size()

        for i in range(11):
            x = i * LANE_WIDTH + LANE_OFFSET
            pygame.draw.line(surface, (200, 200, 200),
                             (x, 0), (x, height))

        for note in self.notes:
            # y좌표 계산식 변경
            y = NOTE_CENTER_Y + (self.music.position - note["time"]) * NOTE_SPEED

            if -NOTE_RADIUS < y < height + NOTE_RADIUS:
                x = note["num"] * LANE_WIDTH + LANE_OFFSET+LANE_WIDTH/2
                pygame.draw.circle(surface, (0, 200, 200), (x, int(y)), NOTE_RADIUS)

        # 가로선 (BPM/마디, 변속 반영)
        if hasattr(self, 'bpm_changes') and self.bpm_changes:
            start_time = self.music.position - (height - NOTE_CENTER_Y) / NOTE_SPEED
            end_time = self.music.position + NOTE_CENTER_Y / NOTE_SPEED

            # bpm_changes를 시간순으로 순회
            bpm_list = sorted(self.bpm_changes, key=lambda c: c["time"])
            for i, change in enumerate(bpm_list):
                bpm = change["bpm"]
                numer, denom = tuple(change.get("time_signature", (4, 4)))

                # 구간 끝은 다음 bpm_change 또는 end_time
                next_time = bpm_list[i + 1]["time"] if i + 1 < len(bpm_list) else end_time

                # 구간 시작은 max(start_time, change["time"])
                seg_start = max(start_time, change["time"])
                seg_end = min(end_time, next_time)

                if seg_start > seg_end:
                    continue

                measure_interval = (60000 / bpm) * (4 / denom) * numer
                beat_interval = (60000 / bpm) * (4 / self.beat_unit)

                # 첫 마디 시작점
                current_measure_time = change["time"]
                while current_measure_time <= seg_end:
                    # 박자 단위 선
                    t = current_measure_time
                    while t < current_measure_time + measure_interval and t <= seg_end:
                        y = NOTE_CENTER_Y + (self.music.position - t) * NOTE_SPEED
                        pygame.draw.line(surface, (100, 100, 100),
                                         (LANE_OFFSET, y),
                                         (LANE_OFFSET + LANE_WIDTH * 10, y))
                        t += beat_interval

                    # 마디선
                    y = NOTE_CENTER_Y + (self.music.position - current_measure_time) * NOTE_SPEED
                    pygame.draw.line(surface, (180, 180, 180),
                                     (LANE_OFFSET, y),
                                     (LANE_OFFSET + LANE_WIDTH * 10, y), 2)

                    current_measure_time += measure_interval

        # 변속도 선 표시
        if hasattr(self, 'bpm_changes'):
            for bpm_change in self.bpm_changes:
                t = bpm_change["time"]
                y = NOTE_CENTER_Y + (self.music.position - t) * NOTE_SPEED
                if -50 < y < height + 50:  # 화면 안에 있는 경우만
                    # 세로선
                    pygame.draw.line(surface, (255, 200, 0),
                                     (LANE_OFFSET, y),
                                     (LANE_OFFSET + LANE_WIDTH * 10, y), 2)
                    # BPM 텍스트
                    bpm_text = myFont.render(str(bpm_change["bpm"]), True, (255, 200, 0))
                    surface.blit(bpm_text, (LANE_OFFSET + LANE_WIDTH * 10 + 10, y - bpm_text.get_height() / 2))

        pygame.draw.line(surface, (255, 255, 255), (0, NOTE_CENTER_Y), (width, NOTE_CENTER_Y), 3)

        for i in range(10):
            x = i * LANE_WIDTH + LANE_OFFSET+LANE_WIDTH/2
            num_text = myFont.render(str(i), True, (255, 255, 255))
            surface.blit(num_text, (x - num_text.get_width() / 2, NOTE_CENTER_Y))

        position_text = myFont.render(str(self.music.position), True, (255, 255, 255))
        surface.blit(position_text, (width/2, 100))
