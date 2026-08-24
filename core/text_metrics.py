"""Измерение реального размера текста через Kivy.

Нужно для точной пагинации под конкретный шрифт/размер экрана — в отличие
от прежнего character-based приближения (N символов на строку), здесь
ширина и высота строк действительно совпадают с тем, что отрисует Kivy
Label. Работает и без запущенного окна/дисплея — text-провайдер Kivy не
требует Window для измерения экстентов, только для рендера на экран.
"""

from __future__ import annotations

from functools import lru_cache

from kivy.core.text import Label as CoreLabel


@lru_cache(maxsize=None)
def _core_label(font_size: float, font_name: str | None) -> CoreLabel:
    # font_name=None должен использовать шрифт Kivy по умолчанию — передавать
    # None явным kwarg-ом нельзя, resolve_font_name() в Kivy на этом падает
    if font_name:
        return CoreLabel(font_size=font_size, font_name=font_name)
    return CoreLabel(font_size=font_size)


@lru_cache(maxsize=50000)
def word_width(word: str, font_size: float, font_name: str | None = None) -> float:
    return _core_label(font_size, font_name).get_extents(word)[0]


def space_width(font_size: float, font_name: str | None = None) -> float:
    return word_width(" ", font_size, font_name)


def line_height(font_size: float, font_name: str | None = None) -> float:
    # "Ag" содержит и выносной элемент, и подстрочный — реалистичная высота строки
    return _core_label(font_size, font_name).get_extents("Ag")[1]
