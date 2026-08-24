"""Движок пагинации: раскладывает Book на страницы под реальный размер
экрана и шрифта.

Перенос строк считается по фактической ширине слов в пикселях (через
core/text_metrics.py), а не по количеству символов — поэтому разбивка на
страницы соответствует тому, что реально отрисует Kivy Label с данным
шрифтом и размером, независимо от того, моноширинный он или нет.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.book_model import Block, BlockType, Book
from core.text_metrics import line_height, space_width, word_width


@dataclass
class Line:
    text: str
    is_heading: bool = False


@dataclass
class Page:
    chapter_index: int
    chapter_title: str
    lines: list[Line] = field(default_factory=list)


def _wrap_words(text: str, max_width: float, font_size: float, font_name: str | None) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    sp_width = space_width(font_size, font_name)
    lines: list[str] = []
    current_words: list[str] = []
    current_width = 0.0

    for word in words:
        w_width = word_width(word, font_size, font_name)
        extra = w_width if not current_words else w_width + sp_width
        if current_words and current_width + extra > max_width:
            lines.append(" ".join(current_words))
            current_words = [word]
            current_width = w_width
        else:
            current_words.append(word)
            current_width += extra

    if current_words:
        lines.append(" ".join(current_words))
    return lines


def _block_to_lines(block: Block, max_width: float, font_size: float, font_name: str | None) -> list[Line]:
    if block.type == BlockType.IMAGE:
        return [Line(text=f"[Изображение: {block.image_ref}]")]

    prefix = "• " if block.type == BlockType.LIST_ITEM else ""
    wrap_width = max_width - word_width(prefix, font_size, font_name) if prefix else max_width
    wrapped = _wrap_words(block.text, max(wrap_width, 1.0), font_size, font_name)

    is_heading = block.type == BlockType.HEADING
    lines = [Line(text=prefix + wrapped[0], is_heading=is_heading)]
    lines.extend(Line(text=(" " * len(prefix)) + w, is_heading=is_heading) for w in wrapped[1:])
    return lines


def paginate(
    book: Book,
    page_width: float,
    page_height: float,
    font_size: float,
    font_name: str | None = None,
) -> list[Page]:
    line_h = line_height(font_size, font_name)
    lines_per_page = max(int(page_height // line_h), 1)

    pages: list[Page] = []
    current_lines: list[Line] = []

    def flush(chapter_index: int, chapter_title: str) -> None:
        nonlocal current_lines
        if current_lines:
            pages.append(Page(chapter_index=chapter_index, chapter_title=chapter_title, lines=current_lines))
            current_lines = []

    for chapter_index, chapter in enumerate(book.chapters):
        for block in chapter.blocks:
            block_lines = _block_to_lines(block, page_width, font_size, font_name)
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
