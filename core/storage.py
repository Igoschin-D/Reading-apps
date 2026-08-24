"""Хранение внутреннего формата книги на диске.

Контейнер .ubook — это zip-архив:
  manifest.json   — метаданные и главы (структура Book.to_dict())
  assets/         — изображения, на которые ссылаются блоки IMAGE
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from core.book_model import Book

MANIFEST_NAME = "manifest.json"


def save_book(book: Book, output_path: str | Path, asset_files: dict[str, bytes] | None = None) -> None:
    asset_files = asset_files or {}
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(MANIFEST_NAME, json.dumps(book.to_dict(), ensure_ascii=False, indent=2))
        for name, data in asset_files.items():
            archive.writestr(f"assets/{name}", data)


def load_book(input_path: str | Path) -> Book:
    with zipfile.ZipFile(input_path, "r") as archive:
        manifest = json.loads(archive.read(MANIFEST_NAME))
    return Book.from_dict(manifest)
