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
threading.Thread(target=tutorial.load, args=(load_info,)).start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    # 진행률 계산
    progress = load_info.progress / load_info.max_progress

    # 프로그래스 바
    pygame.draw.rect(screen, (255, 255, 255), (50, 180, 500, 30), 2)
    pygame.draw.rect(screen, (0, 200, 0), (52, 182, 496*progress, 26))

    # 텍스트
    text = font.render(
        f"{load_info.description} ({load_info.progress}/{load_info.max_progress})",
        True, (255, 255, 255)
    )
    screen.blit(text, (50, 140))

    pygame.display.flip()

