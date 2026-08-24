"""Движок пагинации: раскладывает Book на страницы фиксированного размера.

Этап 3 плана. Первая версия работает в терминах символов на строку и
строк на страницу (character-based reflow) — этого достаточно, чтобы
проверить логику навигации без привязки к UI. В Этапе 4, когда появится
Kivy-экран, обёртка над реальным виджетом будет делать pixel-based
перенос строк под фактический размер экрана и шрифта, но останется той
же по интерфейсу: paginate(book, ...) -> list[Page].
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field

from core.book_model import Block, BlockType, Book


@dataclass
class Line:
    text: str
    is_heading: bool = False


@dataclass
class Page:
    chapter_index: int
    chapter_title: str
    lines: list[Line] = field(default_factory=list)


def _block_to_lines(block: Block, chars_per_line: int) -> list[Line]:
    if block.type == BlockType.IMAGE:
        return [Line(text=f"[Изображение: {block.image_ref}]")]

    prefix = "• " if block.type == BlockType.LIST_ITEM else ""
    wrap_width = max(chars_per_line - len(prefix), 1)
    wrapped = textwrap.wrap(block.text, width=wrap_width) or [""]

    is_heading = block.type == BlockType.HEADING
    lines = [Line(text=prefix + wrapped[0], is_heading=is_heading)]
    lines.extend(Line(text=(" " * len(prefix)) + w, is_heading=is_heading) for w in wrapped[1:])
    return lines


def paginate(book: Book, chars_per_line: int, lines_per_page: int) -> list[Page]:
    pages: list[Page] = []
    current_lines: list[Line] = []

    def flush(chapter_index: int, chapter_title: str) -> None:
        nonlocal current_lines
        if current_lines:
            pages.append(Page(chapter_index=chapter_index, chapter_title=chapter_title, lines=current_lines))
            current_lines = []

    for chapter_index, chapter in enumerate(book.chapters):
        for block in chapter.blocks:
            block_lines = _block_to_lines(block, chars_per_line)
            if block.type == BlockType.HEADING and current_lines:
                block_lines = [Line(text="")] + block_lines

            for line in block_lines:
                if len(current_lines) >= lines_per_page:
                    flush(chapter_index, chapter.title)
                current_lines.append(line)

            # пустая строка-разделитель между блоками
            if len(current_lines) >= lines_per_page:
                flush(chapter_index, chapter.title)
            current_lines.append(Line(text=""))

        flush(chapter_index, chapter.title)

    return pages
