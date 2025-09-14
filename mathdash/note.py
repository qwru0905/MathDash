import pygame
import matplotlib
matplotlib.use("Agg")  # GUI 백엔드 없이 그림 저장 가능
import matplotlib.pyplot as plt
import io


def render_text(text, fontsize=24):
    # 임시 Figure 생성 후 bbox 계산
    fig = plt.figure()
    plt.rcParams["mathtext.fontset"] = "stix"
    text_obj = plt.text(0, 0, text, fontsize=fontsize)
    fig.canvas.draw()
    bbox = text_obj.get_window_extent()
    _width, _height = bbox.width / fig.dpi, bbox.height / fig.dpi
    plt.close(fig)

    # 텍스트 크기에 맞춘 Figure 생성
    fig = plt.figure(figsize=(_width, _height))
    plt.text(0.5, 0.5, text, fontsize=fontsize, ha='center', va='center')
    plt.axis("off")

    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", dpi=fig.dpi, transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)

    return pygame.image.load(buf, "image.png")


# 핸들러 정의
handlers = {
    "text": lambda eq: render_text(eq["text"]),
    "equation": lambda eq: render_text(f"${eq['equation']}$"),
    "image": lambda eq: pygame.image.load(eq["path"]),
}


class Note:
    def __init__(self, num: int, equation: dict, time: int, speed: int, x: int, y: int, size: int = 80):
        self._num = num
        self._equation = handlers.get(equation["type"], lambda eq: None)(equation)
        self._time = time
        self._speed = speed
        self._x = x
        self._y = y
        self._size = size

        # 이미지 크기 조정
        max_size = self._size
        w, h = self._equation.get_size()
        if w > max_size or h > max_size:
            scale_factor = min(max_size / w, max_size / h)
            new_size = (int(w * scale_factor), int(h * scale_factor))
            self._equation = pygame.transform.smoothscale(self._equation, new_size)
        w, h = self._equation.get_size()

        # 원형 배경 + 테두리
        self._radius = int(self._size / 2)
        self._bg_surface = pygame.Surface((self._size, self._size), pygame.SRCALPHA)
        pygame.draw.circle(self._bg_surface, (255, 182, 193), (self._radius, self._radius), self._radius)
        pygame.draw.circle(self._bg_surface, (0, 0, 0), (self._radius, self._radius), self._radius, 5)

        # 텍스트 배경 + 테두리
        padding = 6
        self._text_bg = pygame.Surface((w + padding*2, h + padding*2), pygame.SRCALPHA)
        bg_color = (255, 255, 200)
        border_color = (0, 0, 0)
        border_thickness = 2
        pygame.draw.rect(self._text_bg, bg_color, (0, 0, w + padding*2, h + padding*2))
        pygame.draw.rect(self._text_bg, border_color, (0, 0, w + padding*2, h + padding*2), border_thickness)
        self._text_bg.blit(self._equation, (padding, padding))

    def set_default_pos(self, time):
        self._y = 50 + (self._time - time) * (self._speed*60)/1000

    def draw(self, screen):
        # 원형 배경
        rect = self._bg_surface.get_rect(center=(self._x, self._y))
        screen.blit(self._bg_surface, rect)
        # 텍스트
        text_rect = self._text_bg.get_rect(center=(self._x, self._y))
        screen.blit(self._text_bg, text_rect)


if __name__ == '__main__':
    width, height = 1360, 768
    pygame.init()
    pygame.display.set_caption("MathDash")
    _screen = pygame.display.set_mode((width, height))

    note = Note(
        1,
        {"type": "equation", "equation": r"\sqrt{4+12}"},
        1000, 5,
        width/2, height/2
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        _screen.fill((255, 255, 255))
        note.draw(_screen)
        pygame.display.flip()
