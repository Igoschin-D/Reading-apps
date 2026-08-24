"""Точка входа мобильного приложения. Этап 4 плана.

Запуск на десктопе для разработки: python3 app/main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from app.library_screen import LibraryScreen
from app.reader_screen import ReaderScreen
from app.settings_screen import SettingsScreen

BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_DIR = BASE_DIR / "library"


class ReaderApp(MDApp):
    def build(self):
        LIBRARY_DIR.mkdir(exist_ok=True)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        sm = ScreenManager()

        library_screen = LibraryScreen(name="library")
        library_screen.library_dir = LIBRARY_DIR
        sm.add_widget(library_screen)

        sm.add_widget(ReaderScreen(name="reader"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm


if __name__ == "__main__":
    ReaderApp().run()
