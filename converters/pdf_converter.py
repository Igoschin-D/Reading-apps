"""Конвертер PDF -> внутренняя модель Book.

Этап 2 плана разработки. Ограничения первой версии:
- Работает только с PDF, у которых есть текстовый слой (сканы без OCR
  не поддерживаются — см. IDEAS.md)
- Если в PDF есть оглавление (TOC), по нему бьём книгу на главы
- Если TOC нет — определяем главы эвристикой по размеру шрифта
  (см. _split_by_heading_heuristic)
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pymupdf

from core.book_model import Block, BlockType, Book, Chapter, Metadata

# насколько крупнее шрифт заголовка должен быть относительно тела текста,
# чтобы считаться заголовком, а не просто акцентом (полужирным и т.п.)
HEADING_MIN_DELTA = 1.0
# заголовки — короткие строки; длинный текст крупным шрифтом (например,
# эпиграф) не должен приниматься за заголовок главы
MAX_HEADING_CHARS = 120
# заголовок конкретного размера должен повториться хотя бы столько раз,
# чтобы считаться разметкой глав, а не разовым текстом (например,
# заголовком на титульном листе)
MIN_CHAPTER_HEADING_COUNT = 2


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
        chapters = _split_by_heading_heuristic(doc, metadata.title)

    doc.close()
    return Book(metadata=metadata, chapters=chapters)


def _extract_page_blocks(page: "pymupdf.Page") -> list[Block]:
    blocks = []
    for block in page.get_text("blocks"):
        text = block[4].strip()
        if text:
            blocks.append(Block(type=BlockType.PARAGRAPH, text=text))
    return blocks


def _extract_page_blocks_with_size(page: "pymupdf.Page") -> list[tuple[str, float]]:
    """Как _extract_page_blocks, но вместе с текстом отдаёт размер шрифта
    (макс. размер среди спанов блока) — нужен для эвристики заголовков."""
    blocks = []
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:  # пропускаем картинки
            continue
        parts = []
        sizes = []
        for line in block.get("lines", []):
            line_text = "".join(span["text"] for span in line["spans"])
            if line_text.strip():
                parts.append(line_text.strip())
            sizes.extend(span["size"] for span in line["spans"] if span["text"].strip())
        text = " ".join(" ".join(parts).split())
        if text and sizes:
            blocks.append((text, max(sizes)))
    return blocks


def _compute_body_size(blocks: list[tuple[str, float]]) -> float:
    """Самый частотный размер шрифта (по суммарной длине текста) — считаем
    его размером шрифта основного текста, а не заголовков."""
    weight: dict[float, int] = defaultdict(int)
    for text, size in blocks:
        weight[round(size, 1)] += len(text)
    return max(weight, key=weight.get) if weight else 0.0


def _pick_chapter_heading_size(
    blocks: list[tuple[str, float]], body_size: float
) -> tuple[float | None, dict[float, int]]:
    """Среди размеров шрифта крупнее тела текста находит те, что похожи на
    заголовки (короткий текст), и выбирает самый ЧАСТО повторяющийся — так
    отличаем регулярную разметку глав (десятки повторов) от разового
    крупного текста вроде заголовка на титульном листе (пара повторов),
    даже если титульный текст крупнее по кеглю."""
    counts: dict[float, int] = defaultdict(int)
    for text, size in blocks:
        rounded = round(size, 1)
        if rounded >= body_size + HEADING_MIN_DELTA and len(text) <= MAX_HEADING_CHARS:
            counts[rounded] += 1

    repeated_sizes = [size for size, count in counts.items() if count >= MIN_CHAPTER_HEADING_COUNT]
    if not repeated_sizes:
        return None, counts
    return max(repeated_sizes, key=lambda size: (counts[size], size)), counts


def _split_by_heading_heuristic(doc: "pymupdf.Document", fallback_title: str) -> list[Chapter]:
    all_blocks = [b for page in doc for b in _extract_page_blocks_with_size(page)]
    if not all_blocks:
        return [Chapter(title=fallback_title, blocks=[])]

    body_size = _compute_body_size(all_blocks)
    chapter_size, heading_counts = _pick_chapter_heading_size(all_blocks, body_size)

    if chapter_size is None:
        # нет ни одного повторяющегося крупного шрифта — не на чем бить
        # книгу на главы, оставляем как есть, одной главой
        blocks = [Block(type=BlockType.PARAGRAPH, text=text) for text, _ in all_blocks]
        return [Chapter(title=fallback_title, blocks=blocks)]

    heading_sizes = set(heading_counts.keys())
    chapters: list[Chapter] = []
    current_blocks: list[Block] = []
    current_title = fallback_title

    def flush() -> None:
        if current_blocks:
            chapters.append(Chapter(title=current_title, blocks=current_blocks))

    for text, size in all_blocks:
        rounded = round(size, 1)
        if rounded >= chapter_size:
            flush()
            current_blocks = [Block(type=BlockType.HEADING, text=text, level=1)]
            current_title = text
        elif rounded in heading_sizes:
            current_blocks.append(Block(type=BlockType.HEADING, text=text, level=2))
        else:
            current_blocks.append(Block(type=BlockType.PARAGRAPH, text=text))

    flush()
    return chapters


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
