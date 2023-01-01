"""
GUI allowing to edit settings, load songs...
"""
import json
import os

import pygame
from faker import Faker

from pypastator.constants import (
    BLACK,
    BLUE,
    DARKEST_GRAY,
    WHITE,
    WIDGET_LINE,
    WIDGETS_MARGIN,
)
from pypastator.widgets.gui.base import GUI
from pypastator.widgets.gui.row import make_row
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator

MODAL_MARGIN = 20
MODAL_BORDER = 3
TOTAL_MODAL_MARGIN = MODAL_MARGIN + MODAL_BORDER
MODAL_ROW_WIDTH = 1024 - (TOTAL_MODAL_MARGIN * 2)


class ModalGUI(GUI):
    """
    A GUI that's displayed over the rest.
    """

    def __init__(self, *a, **kw):
        self.sub_menus = {}
        super().__init__(*a, **kw)

    def redraw(self):
        surf = pygame.display.get_surface()
        surf.fill(
            WHITE,
            (
                MODAL_MARGIN,
                MODAL_MARGIN,
                1024 - (MODAL_MARGIN * 2),
                768 - (MODAL_MARGIN * 2),
            ),
        )
        surf.fill(
            DARKEST_GRAY,
            (
                TOTAL_MODAL_MARGIN,
                TOTAL_MODAL_MARGIN,
                1024 - ((TOTAL_MODAL_MARGIN) * 2),
                768 - ((TOTAL_MODAL_MARGIN) * 2),
            ),
        )
        super().redraw()

    def init_widgets(self):
        pass

    def any_visible(self):
        """
        True if self is visible or any of its submenus.
        """
        return (
            self.visible or
            any(sub.visible for sub in self.sub_menus.values())
        )

    def update_widgets(self):
        """
        Should be implemented by sub-classes.
        """
        raise NotImplementedError

    def show(self):
        """
        Show this GUI hide its submenus.
        """
        for submenu in self.sub_menus.values():
            if submenu.visible:
                submenu.hide()
        if self.visible:
            return
        super().show()
        self.update_widgets()

    def handle_click(self, *a, **kw):
        if self.visible:
            super().handle_click(*a, **kw)
        else:
            for submenu in self.sub_menus.values():
                submenu.handle_click(*a, **kw)

    def handle_tick(self, *a, **kw):
        if self.visible:
            super().handle_tick(*a, **kw)
        else:
            for submenu in self.sub_menus.values():
                submenu.handle_tick(*a, **kw)

    def handle_cc(self, cc_channel, cc_number, cc_value):
        if cc_value != 127:
            return
        if cc_number == 7:
            if self.visible:
                self.hide()
                if not isinstance(self, SettingsGUI):
                    self.model.settings_menu.show()
                    self.model.settings_menu.activate_next()
        if self.visible:
            super().handle_cc(cc_channel, cc_number, cc_value)
        else:
            for submenu in self.sub_menus.values():
                submenu.handle_cc(cc_channel, cc_number, cc_value)

    def hide(self):
        for submenu in self.sub_menus.values():
            submenu.hide()
        if not self.visible:
            return
        # Shade the whole UI
        surf = pygame.display.get_surface()
        rect = pygame.Rect(0, 0, 1024, 768)
        surf.fill(BLACK, rect)
        super().hide()

    def show_submenu(self, submenu):
        """
        Hide this menu and show said submenu.
        """
        self.hide()
        self.sub_menus[submenu].show()
        self.sub_menus[submenu].activate_next()


class SettingsGUI(ModalGUI):
    """
    Settings GUI (to select MIDI devices, load songs...)
    """

    def init_widgets(self):
        """
        Initialize GUI's widgets.
        """
        kwargs = dict(visible=False)
        for btn_id, btn_label in {
            "new_song": "New",
            "load_song": "Load...",
            "save_song": "Save",
            "rename_song": "Name..."
        }.items():
            self.widgets[btn_id] = Label(text=btn_label, **kwargs)
            self.widgets[btn_id].on_click = self.click_callback_maker(btn_id)
            self.activable_widgets.append(btn_id)
        self.sub_menus["load_song"] = LoadSongGUI(self.model)
        self.sub_menus["rename_song"] = SaveAsGUI(self.model)

    def update_widgets(self):
        """
        Update widgets position or details.
        """
        pos_y = TOTAL_MODAL_MARGIN
        pos_x = TOTAL_MODAL_MARGIN
        self.widgets["songs_header"] = Separator(
            text="Songs",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["song_title"] = Label(
            text=self.model.get_title(),
            visible=False,
            width=MODAL_ROW_WIDTH,
            bcolor=BLUE,
        )
        make_row(
            [self.widgets["song_title"]],
            pos_x=pos_x,
            pos_y=pos_y,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        make_row(
            [
                self.widgets["new_song"],
                self.widgets["load_song"],
                self.widgets["save_song"],
                self.widgets["rename_song"],
            ],
            pos_x=pos_x,
            pos_y=pos_y,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["settings_header"] = Separator(
            text="Settings",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=MODAL_ROW_WIDTH,
        )

    def click_callback_maker(self, btn_id):
        """
        Prepare a callback for the on click event.
        """

        def callback(_val, _b):
            self.activate_widget(btn_id)
            self.increment()

        return callback

    def increment(self, *_a, widget_name=None, **_kw):
        if widget_name is not None:
            self.activate_widget(widget_name)
        if self.active_widget == "new_song":
            self.hide()
            self.model.new_song()
        elif self.active_widget == "load_song":
            self.show_submenu("load_song")
        elif self.active_widget == "save_song":
            self.hide()
            self.model.save()
        elif self.active_widget == "rename_song":
            self.show_submenu("rename_song")

class LoadSongGUI(ModalGUI):
    """
    List the saved songs and allow to load one.
    """

    def update_widgets(self):
        """
        List songs.
        """
        pos_y = TOTAL_MODAL_MARGIN
        pos_x = TOTAL_MODAL_MARGIN
        self.widgets["songs_header"] = Separator(
            text="Load song",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        for fname in os.listdir("songs"):
            if fname.endswith(".json"):
                with open(
                    os.path.join("songs", fname), "r", encoding="utf8"
                ) as file_pointer:
                    data = json.load(file_pointer)
                    title = data.get("title", fname)
                    widget = Label(
                        text=title,
                        visible=False,
                        width=MODAL_ROW_WIDTH,
                    )
                    widget.on_click = self.song_loader(fname)
                    make_row(
                        [widget],
                        pos_x=pos_x,
                        pos_y=pos_y,
                        width=MODAL_ROW_WIDTH,
                    )
                    self.widgets[fname] = widget
                    self.activable_widgets.append(fname)
                    pos_y += WIDGET_LINE + WIDGETS_MARGIN

    def song_loader(self, filename):
        """
        Prepare a callback for the on click event.
        """

        def callback(_val, _b):
            self.activate_widget(filename)
            self.increment()

        return callback

    def increment(self, *_a):
        filename = self.active_widget
        self.hide()
        self.model.load(filename)


class SaveAsGUI(ModalGUI):
    """
    Allow choosing a title for the song and saving it.
    """

    def update_widgets(self):
        """
        List songs.
        """
        pos_y = TOTAL_MODAL_MARGIN
        pos_x = TOTAL_MODAL_MARGIN
        self.widgets["header"] = Separator(
            text="Current song title",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["song_title"] = Label(
            text=self.model.get_title(),
            visible=False,
            width=MODAL_ROW_WIDTH,
            bcolor=BLUE,
        )
        make_row(
            [self.widgets["song_title"]],
            pos_x=pos_x,
            pos_y=pos_y,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["header2"] = Separator(
            text="Choose a generated title below",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=MODAL_ROW_WIDTH,
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        fake = Faker()
        for widget_name, value in {
            "fake_text": fake.text(max_nb_chars=40),
            "fake_catch_phrase": fake.catch_phrase(),
            "fake_name": fake.name(),
            "fake_text2": fake.text(max_nb_chars=40),
            "fake_catch_phrase2": fake.catch_phrase(),
            "fake_name2": fake.name(),
        }.items():
            self.widgets[widget_name] = Label(
                text=value,
                visible=False,
                width=MODAL_ROW_WIDTH,
            )
            self.widgets[widget_name].on_click = self.title_setter(widget_name)
            make_row(
                [self.widgets[widget_name]],
                pos_x=pos_x,
                pos_y=pos_y,
                width=MODAL_ROW_WIDTH,
            )
            self.activable_widgets.append(widget_name)
            pos_y += WIDGET_LINE + WIDGETS_MARGIN

    def title_setter(self, widget_name):
        """
        Prepare a callback for the on click event.
        """

        def callback(_val, _b):
            self.activate_widget(widget_name)
            self.increment()

        return callback

    def increment(self, *_a):
        value = self.widgets[self.active_widget].text
        self.model.set_title(value)
        self.widgets["song_title"].set_text(self.model.get_title())
