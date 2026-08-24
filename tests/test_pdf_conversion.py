"""Ручной прогон конвертера PDF на тестовой книге (Этап 2 плана).

Запуск: python3 tests/test_pdf_conversion.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from converters.pdf_converter import convert
from core.storage import load_book, save_book

SAMPLE_PDF = Path(__file__).resolve().parent.parent / "samples" / "test_book.pdf"
OUTPUT_UBOOK = Path(__file__).resolve().parent.parent / "samples" / "test_book.ubook"


def main() -> None:
    print(f"Конвертирую: {SAMPLE_PDF}")
    book = convert(SAMPLE_PDF)

    print(f"\nМетаданные: title={book.metadata.title!r}, author={book.metadata.author!r}")
    print(f"Глав: {len(book.chapters)}")
    for chapter in book.chapters:
        print(f"  - {chapter.title!r}: {len(chapter.blocks)} блоков")

    save_book(book, OUTPUT_UBOOK)
    print(f"\nСохранено во внутренний формат: {OUTPUT_UBOOK}")

    reloaded = load_book(OUTPUT_UBOOK)
    assert reloaded.to_dict() == book.to_dict(), "Book после load_book не совпадает с оригиналом!"
    print("Проверка round-trip (save -> load) пройдена.")

    print("\n--- Превью первых 5 блоков первой главы ---")
    for block in book.chapters[0].blocks[:5]:
        preview = block.text.replace("\n", " ")[:80]
        print(f"[{block.type.value}] {preview}")


if __name__ == "__main__":
    main()
