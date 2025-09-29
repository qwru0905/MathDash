import pygame


def normalize_mods(mods):
    out = 0
    if mods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL):
        out |= pygame.KMOD_CTRL
    if mods & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT):
        out |= pygame.KMOD_SHIFT
    if mods & (pygame.KMOD_LALT | pygame.KMOD_RALT):
        out |= pygame.KMOD_ALT
    if mods & (pygame.KMOD_LMETA | pygame.KMOD_RMETA):
        out |= pygame.KMOD_META
    return out


class Shortcut:
    def __init__(self, key, mods, callback):
        """
        key: pygame.K_* (예: pygame.K_s)
        mods: modifier 조합 (예: pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
        """
        self.key = key
        self.mods = mods
        self.callback = callback

    def check(self, event):
        if not self.callback:
            return
        if event.type == pygame.KEYDOWN:
            normal_mod = normalize_mods(event.mod)

            if event.key != self.key:
                return  # 안 눌렸으면 바로 종료

            if normal_mod != self.mods:
                return

            modifier_keys = {
                pygame.K_LCTRL, pygame.K_RCTRL,
                pygame.K_LSHIFT, pygame.K_RSHIFT,
                pygame.K_LALT, pygame.K_RALT,
                pygame.K_LMETA, pygame.K_RMETA
            }

            pressed = pygame.key.get_pressed()
            # self.key와 수식 키를 제외한 다른 키가 눌렸는지 확인
            for key_code in range(len(pressed)):
                # 현재 키가 눌렸고, self.key가 아니고, 수식 키도 아닐 경우
                if pressed[key_code] and key_code != self.key and key_code not in modifier_keys:
                    return  # 다른 일반 키가 눌렸으므로 함수 종료

            self.callback()


class ShortcutManager:
    def __init__(self):
        self.shortcuts = []

    def add(self, key, mod, callback):
        self.shortcuts.append(Shortcut(key, mod, callback))

    def handle_event(self, event):
        for sc in self.shortcuts:
            sc.check(event)
