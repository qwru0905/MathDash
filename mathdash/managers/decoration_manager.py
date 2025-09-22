import pygame
from dataclasses import dataclass, field
from .utils import hex_to_rgb, opacity_to_alpha


@dataclass
class Decoration:
    tags: list[str]
    surface: pygame.Surface
    pos: tuple[int, int]
    pos_offset: list[int] = field(default_factory=lambda: [0, 0])
    rotation: float = 0.0
    scale: list[int] = field(default_factory=lambda: [100, 100])
    depth: int = 0
    opacity: int = 100

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


class DecorationManager:
    def __init__(self):
        self.decorations: list[Decoration] = []
        self.tag_map: dict[str, list[Decoration]] = {}

    def load_from_json(self, decorations_data: list[dict], font: pygame.font.Font, load_info):
        for dec in decorations_data:
            if dec["type"] == "text":
                rgb = hex_to_rgb(dec.get("color", "ffffff"))
                surface = font.render(dec["text"], True, rgb).convert_alpha()

                deco = Decoration(
                    tags=dec.get("tag", "").split(),
                    surface=surface,
                    pos=tuple(dec.get("pos", (0, 0))),
                    rotation=dec.get("rotation", 0),
                    scale=dec.get("scale", [100, 100]),
                    depth=dec.get("depth", 0),
                    opacity=dec.get("opacity", 100),
                )
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

    def draw(self, screen: pygame.Surface):
        for deco in sorted(self.decorations, key=lambda d: d.depth):
            deco.render(screen)
