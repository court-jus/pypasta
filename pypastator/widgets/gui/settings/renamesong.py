"""
GUI allowing to rename a song.
"""
from faker import Faker

from pypastator.constants import BLUE, WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.session import BaseSessionGUI
from pypastator.widgets.gui.settings.modalgui import ModalGUI
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class RenameSongGUI(ModalGUI, BaseSessionGUI):
    """
    Allow choosing a title for the song.
    """

    def update_widgets(self):
        """
        List songs.
        """
        pos_x, pos_y = self.get_base_xy()
        self.widgets["header"] = Separator(
            text="Current song title",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=self.get_row_width(),
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["song_title"] = Label(
            text=self.model.get_title(),
            visible=False,
            width=self.get_row_width(),
            bcolor=BLUE,
        )
        self.make_row(
            [self.widgets["song_title"]],
            pos_x=pos_x,
            pos_y=pos_y,
            width=self.get_row_width(),
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["header2"] = Separator(
            text="Choose a generated title below",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=self.get_row_width(),
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
                width=self.get_row_width(),
            )
            self.widgets[widget_name].on_click = self.title_setter(widget_name)
            self.make_row(
                [self.widgets[widget_name]],
                pos_x=pos_x,
                pos_y=pos_y,
                width=self.get_row_width(),
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
