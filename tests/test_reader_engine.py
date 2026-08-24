"""Ручной прогон движка чтения на тестовой книге (Этап 3 плана).

Запуск: python3 tests/test_reader_engine.py
Предполагает, что samples/test_book.ubook уже создан
(python3 tests/test_pdf_conversion.py).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.reader import BookReader
from core.storage import load_book

UBOOK_PATH = Path(__file__).resolve().parent.parent / "samples" / "test_book.ubook"


def print_page(page, index, total) -> None:
    print(f"\n===== Страница {index + 1}/{total} | глава: {page.chapter_title!r} =====")
    for line in page.lines:
        print(line.text)


def main() -> None:
    book = load_book(UBOOK_PATH)

    # эмулируем маленький экран телефона: 360x640px, шрифт 16sp
    reader = BookReader(book, page_width=360, page_height=640, font_size=16)
    print(f"Всего страниц: {reader.total_pages()}")
    print(f"Оглавление: {reader.table_of_contents()}")

    print_page(reader.current_page(), reader.current_index, reader.total_pages())

    page = reader.next_page()
    if page:
        print_page(page, reader.current_index, reader.total_pages())

    page = reader.prev_page()
    print("\n-- prev_page() вернул на страницу 1, совпадает с исходной:",
          page is not None and reader.current_index == 0)


if __name__ == "__main__":
    main()
