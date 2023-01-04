"""
GUI allowing to rename a song.
"""
from faker import Faker

from pypastator.constants import BLUE, WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.row import make_row
from pypastator.widgets.gui.settings.modalgui import (
    MODAL_ROW_WIDTH,
    TOTAL_MODAL_MARGIN,
    ModalGUI,
)
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class RenameSongGUI(ModalGUI):
    """
    Allow choosing a title for the song.
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
