"""
GUI allowing to edit settings, load songs...
"""

from pypastator.constants import BLUE, WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.session import BaseSessionGUI
from pypastator.widgets.gui.settings.loadsong import LoadSongGUI
from pypastator.widgets.gui.settings.mididevice import (
    AddMidiCtrlDevice,
    AddMidiOutputDevice,
    SetMidiClockDevice,
)
from pypastator.widgets.gui.settings.modalgui import ModalGUI
from pypastator.widgets.gui.settings.renamesong import RenameSongGUI
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class SettingsGUI(ModalGUI, BaseSessionGUI):
    """
    Settings GUI (to select MIDI devices, load songs...)
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.is_main_settings_gui = True

    def init_widgets(self):
        """
        Initialize GUI's widgets.
        """
        kwargs = dict(visible=False)
        for btn_id, btn_label in {
            "new_song": "New",
            "load_song": "Load...",
            "save_song": "Save",
            "rename_song": "Name...",
        }.items():
            self.widgets[btn_id] = Label(text=btn_label, **kwargs)
            self.widgets[btn_id].on_click = self.click_callback_maker(btn_id)
            self.activable_widgets.append(btn_id)
        self.sub_menus["load_song"] = LoadSongGUI(self.model)
        self.sub_menus["rename_song"] = RenameSongGUI(self.model)
        self.sub_menus["add_midi_output"] = AddMidiOutputDevice(
            self.model, header="Select MIDI output device", input_output="output"
        )
        self.sub_menus["add_midi_ctrl"] = AddMidiCtrlDevice(
            self.model, header="Select MIDI controller device", input_output="input"
        )
        self.sub_menus["set_midi_clock"] = SetMidiClockDevice(
            self.model, header="Select MIDI clock device", input_output="input"
        )

    def update_widgets(self):
        """
        Update widgets position or details.
        """
        pos_x, pos_y = self.get_base_xy()
        line_height = WIDGET_LINE + WIDGETS_MARGIN
        self.widgets["songs_header"] = Separator(
            text="Songs",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=self.get_row_width(),
        )
        pos_y += line_height
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
        pos_y += line_height
        self.make_row(
            [
                self.widgets["new_song"],
                self.widgets["load_song"],
                self.widgets["save_song"],
                self.widgets["rename_song"],
            ],
            pos_x=pos_x,
            pos_y=pos_y,
            width=self.get_row_width(),
        )
        pos_y += line_height
        self.widgets["settings_header"] = Separator(
            text="Settings",
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=self.get_row_width(),
        )
        pos_y += line_height
        row = []
        for widget_name, label in {
            "add_midi_output": "Add MIDI output",
            "add_midi_ctrl": "Add MIDI controller",
            "set_midi_clock": "Set MIDI clock",
        }.items():
            self.widgets[widget_name] = Label(
                text=label,
                visible=False,
            )
            self.widgets[widget_name].on_click = self.click_callback_maker(widget_name)
            self.activable_widgets.append(widget_name)
            row.append(widget_name)
        self.make_row(
            [self.widgets[widget_name] for widget_name in row],
            pos_x=pos_x,
            pos_y=pos_y,
            width=self.get_row_width(),
        )
        pos_y += line_height

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
        elif self.active_widget == "save_song":
            self.hide()
            self.model.save()
        elif self.active_widget in self.sub_menus:
            self.show_submenu(self.active_widget)
