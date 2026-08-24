"""Сессия чтения: навигация по страницам поверх Paginator.

UI (Этап 4) будет дергать только этот класс — не Book и не Paginator
напрямую.
"""

from __future__ import annotations

from core.book_model import Book
from core.paginator import Page, paginate


class BookReader:
    def __init__(
        self,
        book: Book,
        page_width: float,
        page_height: float,
        font_size: float,
        font_name: str | None = None,
    ):
        self.book = book
        self.pages: list[Page] = paginate(book, page_width, page_height, font_size, font_name)
        self.current_index = 0

    def total_pages(self) -> int:
        return len(self.pages)

    def current_page(self) -> Page:
        return self.pages[self.current_index]

    def next_page(self) -> Page | None:
        if self.current_index + 1 >= len(self.pages):
            return None
        self.current_index += 1
        return self.current_page()

    def prev_page(self) -> Page | None:
        if self.current_index - 1 < 0:
            return None
        self.current_index -= 1
        return self.current_page()

    def go_to_chapter(self, chapter_index: int) -> Page | None:
        for i, page in enumerate(self.pages):
            if page.chapter_index == chapter_index:
                self.current_index = i
                return self.current_page()
        return None

    def table_of_contents(self) -> list[tuple[int, str]]:
        return [(i, chapter.title) for i, chapter in enumerate(self.book.chapters)]
