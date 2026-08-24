"""Единая внутренняя модель книги.

Любой конвертер формата (PDF, FB2, EPUB, ...) должен на выходе отдавать
объект Book. Движок чтения работает только с этой моделью и ничего не
знает про исходный формат файла.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class BlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    IMAGE = "image"
    LIST_ITEM = "list_item"


@dataclass
class Block:
    type: BlockType
    text: str = ""
    level: int = 0          # для HEADING: уровень заголовка (1, 2, 3...)
    image_ref: str = ""     # для IMAGE: имя файла в assets/


@dataclass
class Chapter:
    title: str
    blocks: list[Block] = field(default_factory=list)


@dataclass
class Metadata:
    title: str = ""
    author: str = ""
    language: str = ""
    source_format: str = ""


@dataclass
class Book:
    metadata: Metadata
    chapters: list[Chapter] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "metadata": {
                "title": self.metadata.title,
                "author": self.metadata.author,
                "language": self.metadata.language,
                "source_format": self.metadata.source_format,
            },
            "chapters": [
                {
                    "title": chapter.title,
                    "blocks": [
                        {
                            "type": block.type.value,
                            "text": block.text,
                            "level": block.level,
                            "image_ref": block.image_ref,
                        }
                        for block in chapter.blocks
                    ],
                }
                for chapter in self.chapters
            ],
        }

    @staticmethod
    def from_dict(data: dict) -> "Book":
        metadata = Metadata(**data["metadata"])
        chapters = [
            Chapter(
                title=chapter["title"],
                blocks=[
                    Block(
                        type=BlockType(block["type"]),
                        text=block.get("text", ""),
                        level=block.get("level", 0),
                        image_ref=block.get("image_ref", ""),
                    )
                    for block in chapter["blocks"]
                ],
            )
            for chapter in data["chapters"]
        ]
        return Book(metadata=metadata, chapters=chapters)
