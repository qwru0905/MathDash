import pygame

pygame.init()
FONT = pygame.font.SysFont(None, 24)


class DropDown:
    def __init__(self, items, x, y, w, h):
        self.items = []
        self.visible = False
        for i, (text, cb) in enumerate(items):
            rect = pygame.Rect(x, y + h * i, w, h)
            self.items.append({"text": text, "rect": rect, "callback": cb})

    def draw(self, surf):
        if not self.visible:
            return
        for item in self.items:
            pygame.draw.rect(surf, (220, 220, 220), item["rect"])
            pygame.draw.rect(surf, (0, 0, 0), item["rect"], 1)
            surf.blit(FONT.render(item["text"], True, (0, 0, 0)),
                      (item["rect"].x + 5, item["rect"].y + 5))

    def handle_event(self, event):
        if not self.visible:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            for item in self.items:
                if item["rect"].collidepoint(event.pos):
                    if item["callback"]:
                        item["callback"]()
                    self.visible = False


class MenuItem:
    def __init__(self, text, x, y, w, h, dropdown_items=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.hover = False
        self.dropdown = None
        if dropdown_items:
            self.dropdown = DropDown(dropdown_items, x, y + h, w, h)

    def draw(self, surf):
        color = (200, 200, 200) if self.hover else (150, 150, 150)
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 1)
        surf.blit(FONT.render(self.text, True, (0, 0, 0)),
                  (self.rect.x + 5, self.rect.y + 5))
        if self.dropdown:
            self.dropdown.draw(surf)

    def handle_event(self, event):
        if self.dropdown:
            self.dropdown.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover and self.dropdown:
                self.dropdown.visible = not self.dropdown.visible
            else:
                # 다른 메뉴 클릭 시 dropdown 닫힘
                if self.dropdown:
                    self.dropdown.visible = False


class MenuBar:
    def __init__(self, menus, height=30):
        self.items = []
        x = 0
        for menu_text, dropdown_items in menus:
            w = 100
            self.items.append(MenuItem(menu_text, x, 0, w, height, dropdown_items))
            x += w

    def draw(self, surf):
        pygame.draw.rect(surf, (100, 100, 100), (0, 0, surf.get_width(), 30))
        for item in self.items:
            item.draw(surf)

    def handle_event(self, event):
        for item in self.items:
            item.handle_event(event)
