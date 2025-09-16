import json
from .stage import *


class TutorialStage(Stage):
    BASE_PATH = "assets/tutorial/"

    def __init__(self):
        super().__init__()
        self.music = GameSound(f"{self.BASE_PATH}music.wav", loop=True)
        with open(f"{self.BASE_PATH}data.json", encoding="utf-8") as f:
            self.data = json.load(f)
        self._info = GameInfo.from_json(self.data)
        self.start_time = self.data.get("start_time", 0)
        self.texts = []  # 표시 중인 텍스트들을 저장
        self.font = pygame.font.SysFont("malgungothic", 30)

    def handle_additional_data(self, data: dict):
        # 추가 데이터가 들어올 때 텍스트 이벤트를 기록할 때 pos, color도 같이 저장
        if data["type"] == "show_text":
            self.texts.append({
                "text": data["text"],
                "time": data["time"],  # 시작 기준 시간 (ms)
                "duration": data["duration"],
                "fade_in": data.get("fade", {}).get("in", 0),
                "fade_out": data.get("fade", {}).get("out", 0),
                "pos": data.get("pos", []),  # 예: [x, y] 또는 [] (기본 위치 사용)
                "color": data.get("color", [])  # 예: [r,g,b] 또는 [] (흰색 기본)
            })

    def draw(self, screen):
        super().draw(screen)

        now = self.position
        sw, sh = screen.get_width(), screen.get_height()
        alive_texts = []

        for t in self.texts:
            elapsed = now - t.get("time", now)
            fade_in = t.get("fade_in", 0)
            fade_out = t.get("fade_out", 0)
            duration = t.get("duration", 0)
            total_time = fade_in + duration + fade_out

            if elapsed > total_time:
                continue  # 표시 시간 끝난 텍스트는 제거

            # 알파값 계산 (0으로 나누는 경우 방지)
            if fade_in > 0 and elapsed < fade_in:  # 페이드 인
                alpha = 255 * (elapsed / fade_in)
            elif fade_out > 0 and elapsed >= (fade_in + duration):  # 페이드 아웃
                fade_elapsed = elapsed - (fade_in + duration)
                alpha = 255 * (1 - (fade_elapsed / fade_out))
            else:
                alpha = 255

            alpha = max(0, min(255, int(alpha)))

            # 컬러 처리 (없으면 흰색)
            col = t.get("color", [])
            if isinstance(col, (list, tuple)) and len(col) >= 3:
                color = (int(col[0]), int(col[1]), int(col[2]))
            else:
                color = (255, 255, 255)

            # 텍스트 렌더링 (convert_alpha로 알파 적용 안전하게)
            screen_text = self.font.render(t["text"], True, color).convert_alpha()
            screen_text.set_alpha(alpha)

            # 위치 처리: pos가 있으면 center 기준으로, 없으면 (sw//2, 50)
            pos = t.get("pos", [])
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                # None이나 비수치가 들어올 수 있으니 방어적으로 처리
                try:
                    x = int(pos[0]) if pos[0] is not None else (sw // 2)
                except Exception:
                    x = sw // 2
                try:
                    y = int(pos[1]) if pos[1] is not None else 50
                except Exception:
                    y = 50
                text_rect = screen_text.get_rect(center=(x, y))
            else:
                text_rect = screen_text.get_rect(center=(sw // 2, 50))

            screen.blit(screen_text, text_rect)
            alive_texts.append(t)

        # 끝난 텍스트 제거
        self.texts = alive_texts



