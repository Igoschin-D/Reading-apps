"""Экран чтения: постраничный показ книги, навигация, оглавление."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar

from core.reader import BookReader
from core.storage import load_book

DEFAULT_FONT_SIZE = 16
BASE_CHARS_PER_LINE = 40
BASE_LINES_PER_PAGE = 20


class ReaderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reader: BookReader | None = None
        self.font_size = DEFAULT_FONT_SIZE
        self._toc_menu = None

        root = MDBoxLayout(orientation="vertical")
        self.toolbar = MDTopAppBar(
            title="",
            left_action_items=[["arrow-left", lambda x: self._back_to_library()]],
            right_action_items=[["format-list-bulleted", lambda x: self._open_toc()]],
        )
        root.add_widget(self.toolbar)

        self.page_label = MDLabel(
            text="",
            halign="left",
            valign="top",
            font_size=f"{self.font_size}sp",
            padding=("12dp", "12dp"),
        )
        self.page_label.bind(size=self._update_text_size)
        scroll = MDScrollView()
        scroll.add_widget(self.page_label)
        root.add_widget(scroll)

        nav_bar = MDBoxLayout(size_hint_y=None, height="56dp")
        prev_btn = MDIconButton(icon="chevron-left")
        prev_btn.bind(on_release=lambda x: self._prev_page())
        self.page_indicator = MDLabel(text="", halign="center")
        next_btn = MDIconButton(icon="chevron-right")
        next_btn.bind(on_release=lambda x: self._next_page())
        nav_bar.add_widget(prev_btn)
        nav_bar.add_widget(self.page_indicator)
        nav_bar.add_widget(next_btn)
        root.add_widget(nav_bar)

        self.add_widget(root)

    def _update_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def load_book(self, ubook_path: Path):
        book = load_book(ubook_path)
        chars_per_line, lines_per_page = self._reflow_params()
        self.reader = BookReader(book, chars_per_line=chars_per_line, lines_per_page=lines_per_page)
        self.toolbar.title = book.metadata.title
        self._render_current_page()

    def _reflow_params(self):
        scale = DEFAULT_FONT_SIZE / self.font_size
        chars_per_line = max(int(BASE_CHARS_PER_LINE * scale), 10)
        lines_per_page = max(int(BASE_LINES_PER_PAGE * scale), 5)
        return chars_per_line, lines_per_page

    def _render_current_page(self):
        if not self.reader:
            return
        page = self.reader.current_page()
        self.page_label.text = "\n".join(line.text for line in page.lines)
        self.page_label.font_size = f"{self.font_size}sp"
        self.page_indicator.text = f"{self.reader.current_index + 1} / {self.reader.total_pages()}"

    def _next_page(self):
        if self.reader and self.reader.next_page():
            self._render_current_page()

    def _prev_page(self):
        if self.reader and self.reader.prev_page():
            self._render_current_page()

    def _open_toc(self):
        if not self.reader:
            return
        items = [
            {
                "text": title,
                "on_release": lambda idx=idx: self._go_to_chapter(idx),
            }
            for idx, title in self.reader.table_of_contents()
        ]
        self._toc_menu = MDDropdownMenu(caller=self.toolbar, items=items, width_mult=4)
        self._toc_menu.open()

    def _go_to_chapter(self, chapter_index: int):
        if self.reader and self.reader.go_to_chapter(chapter_index):
            self._render_current_page()
        if self._toc_menu:
            self._toc_menu.dismiss()

    def _back_to_library(self):
        self.manager.current = "library"

    def apply_font_size(self, font_size: int):
        if not self.reader:
            self.font_size = font_size
            return
        current_chapter = self.reader.current_page().chapter_index
        self.font_size = font_size
        chars_per_line, lines_per_page = self._reflow_params()
        self.reader = BookReader(self.reader.book, chars_per_line=chars_per_line, lines_per_page=lines_per_page)
        self.reader.go_to_chapter(current_chapter)
        self._render_current_page()
