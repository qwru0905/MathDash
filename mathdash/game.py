import threading
import pygame

from mathdash.stage import *


class Game:
    def __init__(self, width: int = 1360, height: int = 768):
        pygame.init()
        pygame.display.set_caption("MathDash")
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont("malgungothic", 30)
        self.clock = pygame.time.Clock()

        # Stage 준비
        self.tutorial = CustomStage()
        self.load_info = LoadInfo()
        threading.Thread(
            target=self.tutorial.load, args=(self.load_info,), daemon=True
        ).start()

        self.loading = True
        self.running = True

    def draw_loading(self):
        self.screen.fill((30, 30, 30))

        # 진행률 계산 (0 division 방지)
        progress = 0
        if self.load_info.max_progress > 0:
            progress = self.load_info.progress / self.load_info.max_progress

        # 프로그래스 바
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 180, 500, 30), 2)
        pygame.draw.rect(self.screen, (0, 200, 0), (52, 182, 496 * progress, 26))

        # 텍스트
        text = self.font.render(
            f"{self.load_info.description} ({self.load_info.progress}/{self.load_info.max_progress})",
            True, (255, 255, 255)
        )
        self.screen.blit(text, (50, 140))

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000  # delta time (초 단위)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.tutorial.event(events)

            if self.loading:
                self.draw_loading()

            if self.load_info.complete and self.loading:
                self.loading = False
                self.tutorial.start()

            if not self.loading:
                self.tutorial.update(dt)
                self.tutorial.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
