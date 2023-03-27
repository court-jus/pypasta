"""
GUI allowing to load songs.
"""
import json
import os

from pypastator.constants import WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.session import BaseSessionGUI
from pypastator.widgets.gui.settings.modalgui import ModalGUI
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class LoadSongGUI(ModalGUI, BaseSessionGUI):
    """
    List the saved songs and allow to load one.
    """

    def update_widgets(self):
        """
        List songs.
        """
        pos_x, pos_y = self.get_base_xy()
        self.widgets["songs_header"] = Separator(
            text="Load song",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=self.get_row_width(),
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
                        width=self.get_row_width(),
                    )
                    widget.on_click = self.song_loader(fname)
                    self.make_row(
                        [widget],
                        pos_x=pos_x,
                        pos_y=pos_y,
                        width=self.get_row_width(),
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
