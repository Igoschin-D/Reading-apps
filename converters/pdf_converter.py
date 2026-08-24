"""Конвертер PDF -> внутренняя модель Book.

Этап 2 плана разработки. Ограничения первой версии:
- Работает только с PDF, у которых есть текстовый слой (сканы без OCR
  не поддерживаются — см. IDEAS.md)
- Если в PDF есть оглавление (TOC), по нему бьём книгу на главы,
  иначе весь документ — одна глава
- Разбивка на параграфы — по текстовым блокам PyMuPDF (группировка
  по вёрстке страницы), без определения заголовков по шрифту
"""

from __future__ import annotations

from pathlib import Path

import pymupdf

from core.book_model import Block, BlockType, Book, Chapter, Metadata


def convert(path: str | Path) -> Book:
    doc = pymupdf.open(path)

    metadata = Metadata(
        title=doc.metadata.get("title") or Path(path).stem,
        author=doc.metadata.get("author") or "",
        language="",
        source_format="pdf",
    )

    toc = doc.get_toc()
    if toc:
        chapters = _split_by_toc(doc, toc)
    else:
        chapters = [_whole_document_as_chapter(doc, metadata.title)]

    doc.close()
    return Book(metadata=metadata, chapters=chapters)


def _extract_page_blocks(page: "pymupdf.Page") -> list[Block]:
    blocks = []
    for block in page.get_text("blocks"):
        text = block[4].strip()
        if text:
            blocks.append(Block(type=BlockType.PARAGRAPH, text=text))
    return blocks


def _whole_document_as_chapter(doc: "pymupdf.Document", title: str) -> Chapter:
    blocks: list[Block] = []
    for page in doc:
        blocks.extend(_extract_page_blocks(page))
    return Chapter(title=title, blocks=blocks)


def _split_by_toc(doc: "pymupdf.Document", toc: list[list]) -> list[Chapter]:
    chapters = []
    for i, (level, title, page_num) in enumerate(toc):
        start_page = page_num - 1
        end_page = (toc[i + 1][2] - 1) if i + 1 < len(toc) else doc.page_count
        blocks: list[Block] = []
        for page_index in range(start_page, end_page):
            blocks.extend(_extract_page_blocks(doc[page_index]))
        chapters.append(Chapter(title=title, blocks=blocks))
    return chapters
