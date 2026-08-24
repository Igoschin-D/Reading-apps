"""Экран библиотеки: список импортированных книг + импорт нового PDF."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar

from converters.pdf_converter import convert
from core.storage import save_book


class LibraryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.library_dir: Path | None = None

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(
            title="Библиотека",
            right_action_items=[["cog", lambda x: self._open_settings()]],
        ))

        self.book_list = MDList()
        scroll = MDScrollView()
        scroll.add_widget(self.book_list)
        root.add_widget(scroll)

        import_button = MDRaisedButton(
            text="Импортировать PDF",
            pos_hint={"center_x": 0.5},
            size_hint_y=None,
            height="48dp",
        )
        import_button.bind(on_release=lambda x: self._open_file_chooser())
        root.add_widget(import_button)

        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh_library()

    def refresh_library(self):
        self.book_list.clear_widgets()
        if not self.library_dir:
            return
        for ubook_path in sorted(self.library_dir.glob("*.ubook")):
            item = OneLineListItem(text=ubook_path.stem)
            item.bind(on_release=lambda x, p=ubook_path: self._open_book(p))
            self.book_list.add_widget(item)

    def _open_file_chooser(self):
        chooser = FileChooserListView(filters=["*.pdf"], path=str(Path.home()))
        popup = Popup(title="Выбери PDF файл", content=chooser, size_hint=(0.9, 0.9))

        def on_submit(chooser_widget, selection, touch):
            if selection:
                popup.dismiss()
                self._import_pdf(Path(selection[0]))

        chooser.bind(on_submit=on_submit)
        popup.open()

    def _import_pdf(self, pdf_path: Path):
        book = convert(pdf_path)
        output_path = self.library_dir / f"{pdf_path.stem}.ubook"
        save_book(book, output_path)
        self.refresh_library()

    def _open_book(self, ubook_path: Path):
        reader_screen = self.manager.get_screen("reader")
        reader_screen.load_book(ubook_path)
        self.manager.current = "reader"

    def _open_settings(self):
        self.manager.current = "settings"
