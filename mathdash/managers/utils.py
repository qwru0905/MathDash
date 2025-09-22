import pygame
from easing_functions import *


# ====== 상수 & 유틸 ======
KEY_TO_NUM = {
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


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def opacity_to_alpha(opacity: float) -> int:
    return int(opacity * 2.55)


def make_ease(ease_type: str, start, end, duration):
    if ease_type == "linear":
        return LinearInOut(start, end, duration)
    elif ease_type == "sinein":
        return SineEaseIn(start, end, duration)
    elif ease_type == "sineinout":
        return SineEaseInOut(start, end, duration)
    elif ease_type == "quadout":
        return QuadEaseOut(start, end, duration)
    else:
        return LinearInOut(start, end, duration)  # fallback
