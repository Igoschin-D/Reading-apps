"""Дымовой тест приложения: прогоняет экраны и делает скриншоты.

Запуск (нужен виртуальный дисплей):
  xvfb-run -a python3 tests/test_app_smoke.py

Сценарий: библиотека -> импорт тестового PDF -> открытие книги ->
пролистывание страницы -> экран настроек. На каждом шаге сохраняется
PNG в samples/screenshots/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kivy.clock import Clock
from kivy.core.window import Window

from app.main import ReaderApp

Window.size = (400, 800)

SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "samples" / "screenshots"
SAMPLE_PDF = Path(__file__).resolve().parent.parent / "samples" / "test_book.pdf"

app = ReaderApp()


def shot(name: str):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    Window.screenshot(name=str(SCREENSHOT_DIR / f"{name}.png"))
    print(f"screenshot saved: {name}")


def step_1_library_empty(dt):
    shot("1_library_empty")

    library_screen = app.root.get_screen("library")
    library_screen._import_pdf(SAMPLE_PDF)


def step_2_library_with_book(dt):
    shot("2_library_with_book")

    library_screen = app.root.get_screen("library")
    ubook_path = next(library_screen.library_dir.glob("*.ubook"))
    library_screen._open_book(ubook_path)


def step_3_reader_page1(dt):
    shot("3_reader_page1")

    reader_screen = app.root.get_screen("reader")
    reader_screen._next_page()


def step_4_reader_page2(dt):
    shot("4_reader_page2")
    app.root.current = "settings"


def step_5_settings(dt):
    shot("5_settings")
    app.stop()


def schedule_steps(dt):
    Clock.schedule_once(step_1_library_empty, 0.3)
    Clock.schedule_once(step_2_library_with_book, 0.8)
    Clock.schedule_once(step_3_reader_page1, 1.3)
    Clock.schedule_once(step_4_reader_page2, 1.8)
    Clock.schedule_once(step_5_settings, 2.3)


Clock.schedule_once(schedule_steps, 0)
app.run()
