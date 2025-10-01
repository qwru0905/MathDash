import os.path

import pygame
import tkinter as tk
from tkinter import filedialog
import json

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

        self.data: dict = {}
        self.base_path = None
        self.file_path = None

        self.running = True

        # 메뉴바
        def on_new():
            print("New clicked!")

        def on_quit():
            print("Quit shortcut pressed! (Ctrl+Q)")

        menus = [
            ("File", [("New", on_new), ("Open", self.open_file), ("Save", self.save_file), ("Save As", self.save_file_as)])
        ]

        self.menubar = MenuBar(menus)
        self.shortcut = ShortcutManager()
        self.shortcut.add(pygame.K_n, pygame.KMOD_CTRL, on_new)                                   # Ctrl+N
        self.shortcut.add(pygame.K_o, pygame.KMOD_CTRL, self.open_file)                           # Ctrl+O
        self.shortcut.add(pygame.K_s, pygame.KMOD_CTRL, self.save_file)                           # Ctrl+S
        self.shortcut.add(pygame.K_s, pygame.KMOD_CTRL | pygame.KMOD_SHIFT, self.save_file_as)    # Ctrl+Shift+S
        self.shortcut.add(pygame.K_q, pygame.KMOD_CTRL, on_quit)

        self.tab_surface = pygame.Surface((1360, 768))
        self.tab = NotePlace(self.tab_surface)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="파일 선택",
            filetypes=(("json 파일", "*.json"), ("모든 파일", "*.*"))
        )

        if file_path:
            self.file_path = file_path
            with open(file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.base_path = os.path.dirname(file_path)
            self.tab.open_file(self.base_path, self.data)

    def sort_data(self):
        if "notes" in self.data:
            self.data["notes"].sort(key=lambda x: x.get("time", 0))
        if "bpm_changes" in self.data:
            self.data["bpm_changes"].sort(key=lambda x: x.get("time", 0))
        if "actions" in self.data:
            self.data["actions"].sort(key=lambda x: x.get("time", 0))

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            title="파일 저장",
            defaultextension=".json",
            filetypes=(("json 파일", "*.json"), ("모든 파일", "*.*"))
        )
        if not file_path:
            return  # 사용자가 저장을 취소한 경우
        self.base_path = os.path.dirname(file_path)
        self.sort_data()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print(f"파일이 {file_path}에 저장되었습니다.")

    def save_file(self):
        if not self.base_path:
            self.save_file_as()
            return
        else:
            file_path = self.file_path

        self.sort_data()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print(f"파일이 {file_path}에 저장되었습니다.")

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

            # update
            self.tab.update()

            # draw
            self.screen.fill((0, 0, 0))

            self.screen.blit(self.tab_surface, (0, 30))

            self.tab.draw()
            self.menubar.draw(self.screen)

            pygame.display.flip()
        pygame.quit()
