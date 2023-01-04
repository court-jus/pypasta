"""
GUI allowing to load songs.
"""
import json
import os

from pypastator.constants import WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.row import make_row
from pypastator.widgets.gui.settings.modalgui import (
    MODAL_ROW_WIDTH,
    TOTAL_MODAL_MARGIN,
    ModalGUI,
)
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


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
