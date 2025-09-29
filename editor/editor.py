import pygame
import tkinter as tk
from tkinter import filedialog

from editor.menubar import MenuBar
from editor.shortcut import ShortcutManager
from editor.tabs.note_place import NotePlace


class Editor:
    def __init__(self):
        # tkinter 초기화 (창 숨김)
        self.root = tk.Tk()
        self.root.withdraw()

        # pygame 초기화
        pygame.init()
        self.screen = pygame.display.set_mode((1360, 798))
        self.clock = pygame.time.Clock()

        self.tab = NotePlace()

        self.running = True

        # 메뉴바
        def on_new():
            print("New clicked!")

        def on_save():
            print("Save clicked!")

        def on_save_as():
            print("Save As")

        def on_quit():
            print("Quit shortcut pressed! (Ctrl+Q)")

        menus = [
            ("File", [("New", on_new), ("Open", self.open_file), ("Save", on_save), ("Save As", on_save_as)])
        ]

        self.menubar = MenuBar(menus)
        self.shortcut = ShortcutManager()
        self.shortcut.add(pygame.K_n, pygame.KMOD_CTRL, on_new)                            # Ctrl+N
        self.shortcut.add(pygame.K_o, pygame.KMOD_CTRL, self.open_file)                           # Ctrl+O
        self.shortcut.add(pygame.K_s, pygame.KMOD_CTRL, on_save)                           # Ctrl+S
        self.shortcut.add(pygame.K_s, pygame.KMOD_CTRL | pygame.KMOD_SHIFT, on_save_as)    # Ctrl+Shift+S
        self.shortcut.add(pygame.K_q, pygame.KMOD_CTRL, on_quit)

        self.tab_surface = pygame.Surface((1360, 768))

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="파일 선택",
            filetypes=(("json 파일", "*.json"), ("모든 파일", "*.*"))
        )

        if file_path:
            self.tab.open_file(file_path)

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0

            # event
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                self.menubar.handle_event(event)
                self.shortcut.handle_event(event)
            self.tab.event(events)

            # draw
            self.screen.fill((0, 0, 0))

            self.screen.blit(self.tab_surface, (0, 30))

            self.tab.draw(self.tab_surface)
            self.menubar.draw(self.screen)

            pygame.display.flip()
        pygame.quit()
