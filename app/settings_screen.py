"""Экран настроек: размер шрифта, светлая/тёмная тема."""

from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider
from kivymd.uix.toolbar import MDTopAppBar


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = MDBoxLayout(orientation="vertical", padding="16dp", spacing="16dp")
        root.add_widget(MDTopAppBar(
            title="Настройки",
            left_action_items=[["arrow-left", lambda x: self._back()]],
        ))

        font_row = MDBoxLayout(size_hint_y=None, height="48dp", spacing="12dp")
        font_row.add_widget(MDLabel(text="Размер шрифта", size_hint_x=0.4))
        self.font_slider = MDSlider(min=10, max=28, value=16)
        self.font_slider.bind(value=self._on_font_size_change)
        font_row.add_widget(self.font_slider)
        root.add_widget(font_row)

        theme_row = MDBoxLayout(size_hint_y=None, height="48dp", spacing="12dp")
        theme_row.add_widget(MDLabel(text="Тёмная тема", size_hint_x=0.4))
        self.theme_switch = MDSwitch()
        self.theme_switch.bind(active=self._on_theme_change)
        theme_row.add_widget(self.theme_switch)
        root.add_widget(theme_row)

        root.add_widget(Widget())  # прижимает контент выше к верху экрана

        self.add_widget(root)

    def _on_font_size_change(self, instance, value):
        reader_screen = self.manager.get_screen("reader")
        reader_screen.apply_font_size(int(value))

    def _on_theme_change(self, instance, active):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if active else "Light"

    def _back(self):
        self.manager.current = "library"
