import pygame
import time
import threading

pygame.init()
screen = pygame.display.set_mode((600, 400))
font = pygame.font.SysFont(None, 30)

assets = ["player.png", "enemy.png", "background.png", "music.mp3"]
loaded_count = 0  # 현재 로드된 파일 수


def load_assets():
    global loaded_count
    for asset in assets:
        time.sleep(1)  # 실제 로드 대신 딜레이
        loaded_count += 1  # 로드 완료 표시


# 로딩 스레드 시작
threading.Thread(target=load_assets).start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    # 진행률 계산
    progress = loaded_count / len(assets)

    # 프로그래스 바
    pygame.draw.rect(screen, (255, 255, 255), (50, 180, 500, 30), 2)
    pygame.draw.rect(screen, (0, 200, 0), (52, 182, 496 * progress, 26))

    # 텍스트
    text = font.render(f"Loading... ({loaded_count}/{len(assets)})", True, (255, 255, 255))
    screen.blit(text, (50, 140))

    pygame.display.flip()
