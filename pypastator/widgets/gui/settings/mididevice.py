"""
Generic GUI to choose a MIDI device.
"""
import pygame.midi

from pypastator.constants import WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.session import BaseSessionGUI
from pypastator.widgets.gui.settings.modalgui import ModalGUI
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class MidiDeviceGUI(ModalGUI, BaseSessionGUI):
    """
    Choose a MIDI device.
    """

    def __init__(self, *a, header=None, input_output="both", **kw):
        super().__init__(*a, **kw)
        self.header = header
        self.input_output = input_output

    def update_widgets(self):
        """
        List songs.
        """
        pos_x, pos_y = self.get_base_xy()
        self.widgets["header"] = Separator(
            text="Select MIDI Device" if self.header is None else self.header,
            pos_x=pos_x,
            pos_y=pos_y,
            visible=False,
            width=self.get_row_width(),
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        for i in range(pygame.midi.get_count()):
            device_info = pygame.midi.get_device_info(i)
            name, is_input, is_output = device_info[1:4]
            if (
                is_input
                and self.input_output in ("input", "both")
                or is_output
                and self.input_output in ("output", "both")
            ):
                self._add_midi_widget(pos_y, name, is_input, i)
                pos_y += WIDGET_LINE + WIDGETS_MARGIN

    def _add_midi_widget(self, pos_y, device_name, is_input, device_id):
        """
        Add a widget for this MIDI device.
        """
        widget_name = f"device:{'input' if is_input else 'output'}:{device_id}"
        widget = Label(
            text=device_name,
            visible=False,
            width=self.get_row_width(),
        )
        widget.on_click = self.select_device(widget_name)
        self.make_row(
            [widget],
            pos_x=self.get_base_xy()[0],
            pos_y=pos_y,
            width=self.get_row_width(),
        )
        self.widgets[widget_name] = widget
        self.activable_widgets.append(widget_name)

    def select_device(self, widget_name):
        """
        Prepare a callback for the on click event.
        """

        def callback(_val, _b):
            self.activate_widget(widget_name)
            self.increment()

        return callback

    def increment(self, *_a):
        self.hide()


class AddMidiOutputDevice(MidiDeviceGUI):
    """
    Adds a Midi output device (for notes).
    """

    def increment(self, *a):
        widget_name = self.active_widget
        direction, device_id = widget_name.split(":")[1:]
        self.model.pasta.add_input_output_device(
            dev_id=int(device_id), device_type="output", direction=direction
        )
        super().increment(*a)


class AddMidiCtrlDevice(MidiDeviceGUI):
    """
    Adds a Midi controller device (for CC).
    """

    def increment(self, *a):
        widget_name = self.active_widget
        direction, device_id = widget_name.split(":")[1:]
        self.model.pasta.add_input_output_device(
            dev_id=int(device_id), device_type="ctrl", direction=direction
        )
        super().increment(*a)


class SetMidiClockDevice(MidiDeviceGUI):
    """
    Sets the MIDI clock device.
    """

    def increment(self, *a):
        widget_name = self.active_widget
        device_id = widget_name.split(":")[2]
        self.model.pasta.set_clock_device(dev_id=int(device_id))
        super().increment(*a)
