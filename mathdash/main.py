import threading
import pygame
import stage
from mathdash.stage.stage import LoadInfo

width: int = 1360
height: int = 768

pygame.init()

pygame.display.set_caption("MathDash")
screen = pygame.display.set_mode((width, height))
font = pygame.font.SysFont("malgungothic", 30)

tutorial = stage.tutorial.TutorialStage()
print(tutorial.info)

load_info = LoadInfo()
threading.Thread(target=tutorial.load, args=(load_info,), daemon=True).start()

loading = True
clock = pygame.time.Clock()  # ⬅ 델타 타임 계산용


def draw_loading():
    screen.fill((30, 30, 30))

    # 진행률 계산 (0 division 방지)
    progress = 0
    if load_info.max_progress > 0:
        progress = load_info.progress / load_info.max_progress

    # 프로그래스 바
    pygame.draw.rect(screen, (255, 255, 255), (50, 180, 500, 30), 2)
    pygame.draw.rect(screen, (0, 200, 0), (52, 182, 496 * progress, 26))

    # 텍스트
    text = font.render(
        f"{load_info.description} ({load_info.progress}/{load_info.max_progress})",
        True, (255, 255, 255)
    )
    screen.blit(text, (50, 140))


running = True
while running:
    dt = clock.tick(60) / 1000  # ⬅ 델타 타임 계산 (초 단위, 최대 60FPS)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    tutorial.event(events)

    if loading:
        draw_loading()

    if load_info.complete and loading:
        loading = False
        tutorial.start()  # 로딩 완료 후 시작

    if not loading:
        tutorial.update(dt)    # ⬅ 델타 타임 적용
        tutorial.draw(screen)  # ⬅ draw를 메인 루프에서 호출

    pygame.display.flip()

pygame.quit()
