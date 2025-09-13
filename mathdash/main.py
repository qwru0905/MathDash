import pygame
from sound import GameSound

width: int = 600
height: int = 400

pygame.init()

pygame.display.set_caption("MathDash")
pygame.display.set_mode((width, height))

music = GameSound("assets/tutorial/music.wav", loop=True)
music.play()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
