from abc import ABC, abstractmethod

import pygame
from dataclasses import dataclass, field
from .utils import hex_to_rgb, opacity_to_alpha


@dataclass
class Decoration(ABC):
    tags: list[str] = ()
    pos: tuple[int, int] = (0, 0)
    surface: pygame.Surface | None = None
    pos_offset: list[int] = field(default_factory=lambda: [0, 0])
    rotation: float = 0.0
    scale: list[int] = field(default_factory=lambda: [100, 100])
    depth: int = 0
    opacity: int = 100
    color: list[int] = field(default_factory=lambda: [255, 255, 255])

    def render(self, screen: pygame.Surface):
        surf = self.surface.copy()
        surf.set_alpha(opacity_to_alpha(self.opacity))

        if self.rotation:
            surf = pygame.transform.rotate(surf, self.rotation)

        if self.scale != [100, 100]:
            w, h = surf.get_size()
            surf = pygame.transform.smoothscale(
                surf, (int(w * self.scale[0] / 100), int(h * self.scale[1] / 100))
            )

        x, y = self.pos
        ox, oy = self.pos_offset
        rect = surf.get_rect(center=(x + ox, y + oy))
        screen.blit(surf, rect)

    def apply_color(self, surf: pygame.Surface) -> pygame.Surface:
        """모든 데코에 공통으로 색상 곱 적용"""
        tint = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        tint.fill((*self.color, 255))  # list → unpack해서 RGBA tuple로
        surf = surf.copy()
        surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return surf

    def set_color(self, new_color: list[int]):
        self.color = new_color
        self.surface = self.make_surface()  # 각 subclass에서 구현

    @abstractmethod
    def make_surface(self):
        pass


@dataclass
class TextDecoration(Decoration):
    text: str = ""
    font: pygame.font.Font | None = None

    def make_surface(self):
        if self.font is None:
            raise ValueError("Font is required for TextDecoration")
        base = self.font.render(self.text, True, (255, 255, 255)).convert_alpha()
        return self.apply_color(base)

    def set_text(self, new_text: str):
        self.text = new_text
        self.surface = self.make_surface()


@dataclass
class ImageDecoration(Decoration):
    image_path: str | None = None

    def make_surface(self):
        if not self.image_path:
            raise ValueError("Image path is required for ImageDecoration")
        base = pygame.image.load(self.image_path).convert_alpha()
        return self.apply_color(base)


class DecorationManager:
    def __init__(self, base_path: str):
        self.decorations: list[Decoration] = []
        self.tag_map: dict[str, list[Decoration]] = {}
        self.base_path = base_path

    def load_from_json(self, decorations_data: list[dict], font: pygame.font.Font, load_info):
        for dec in decorations_data:
            if dec["type"] == "text":
                rgb = hex_to_rgb(dec.get("color", "ffffff"))
                deco = TextDecoration(
                    tags=dec.get("tag", "").split(),
                    pos=tuple(dec.get("pos", (0, 0))),
                    text=dec["text"],
                    rotation=dec.get("rotation", 0),
                    scale=dec.get("scale", [100, 100]),
                    depth=dec.get("depth", 0),
                    opacity=dec.get("opacity", 100),
                    font=font,
                    color=rgb,
                )
                deco.surface = deco.make_surface()
                self.add_decoration(deco)

            if dec["type"] == "image":
                rgb = hex_to_rgb(dec.get("color", "ffffff"))
                deco = ImageDecoration(
                    tags=dec.get("tag", "").split(),
                    pos=tuple(dec.get("pos", (0, 0))),
                    rotation=dec.get("rotation", 0),
                    scale=dec.get("scale", [100, 100]),
                    depth=dec.get("depth", 0),
                    opacity=dec.get("opacity", 100),
                    color=rgb,
                    image_path=self.base_path + dec.get("path")
                )
                deco.surface = deco.make_surface()
                self.add_decoration(deco)

            load_info.progress += 1

    def add_decoration(self, deco: Decoration):
        self.decorations.append(deco)
        for tag in deco.tags:
            self.tag_map.setdefault(tag, []).append(deco)

    def find_by_tags(self, tags: str | list[str]) -> list[Decoration]:
        if isinstance(tags, str):
            tags = tags.split()
        result, seen = [], set()
        for tag in tags:
            for deco in self.tag_map.get(tag, []):
                if id(deco) not in seen:
                    seen.add(id(deco))
                    result.append(deco)
        return result

    def draw(self, screen, before):
        for deco in sorted(self.decorations, key=lambda d: -d.depth):
            if not before and deco.depth >= 0:
                deco.render(screen)
            elif before and deco.depth < 0:
                deco.render(screen)
