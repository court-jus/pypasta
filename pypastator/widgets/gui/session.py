"""
GUIs for the Session model.
"""
from pypastator.constants import (
    BAR,
    BEAT,
    DARK_GRAY,
    GREEN,
    WIDGET_LINE,
    WIDGETS_MARGIN,
)
from pypastator.widgets.gui.base import GUI
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class BaseSessionGUI(GUI):
    """
    All GUIs that have a session as model.
    """

    def make_row(self, *a, **kw):
        if "width" not in kw:
            kw["width"] = self.model.pasta.screen_width
        super().make_row(*a, **kw)


class SessionGUI(BaseSessionGUI):
    """
    GUI for the Session model.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.default_widget = "chord"
        self.activable_widgets = ["root_note", "scale", "chord"]

    def init_widgets(self):
        """
        Initialize GUI's widgets.
        """
        pos_y = self.pos_y
        rows_size = self.model.pasta.screen_width - 48
        self.hideable = False
        self.widgets["separator"] = Separator(
            pos_y=pos_y,
            visible=False,
            width=self.model.pasta.screen_width,
        )
        pos_y += WIDGETS_MARGIN
        # Metronome
        self.widgets["metronome"] = Label(
            text="",
            bcolor_selected=GREEN,
            fcolor_selected=DARK_GRAY,
            width=48 - WIDGETS_MARGIN,
            height=2 * WIDGET_LINE - WIDGETS_MARGIN,
            visible=False,
            pos_y=pos_y,
            pos_x=rows_size,
        )
        # Rows
        self.widgets["root_label"] = Label(text="Root", visible=False)
        self.widgets["root_note"] = Label(text="", visible=False)
        self.widgets["root_note"].hook(
            self.model,
            "root_note",
            "menu",
            set_text=True,
            value_getter=lambda: self.model.root_note_str,
        )
        self.widgets["root_note"].on_click = lambda _v, _b: (
            self.activate_widget("root_note"),
            self.model.scale.increment(),
        )
        self.widgets["scale_label"] = Label(text="Scale", visible=False)
        self.widgets["scale"] = Label(text="", visible=False)
        for fieldname in ("scale", "root_note"):
            self.widgets["scale"].hook(
                self.model,
                fieldname,
                f"{fieldname}_to_scale",
                set_text=True,
                value_getter=lambda: self.model.scale_str,
            )
        self.widgets["scale"].on_click = lambda _v, _b: (
            self.activate_widget("scale"),
            self.model.scale.increment(),
        )
        self.make_row(
            [
                self.widgets[widget_name]
                for widget_name in (
                    "root_label",
                    "root_note",
                    "scale_label",
                    "scale",
                )
            ],
            pos_y=pos_y,
            width=rows_size,
        )
        # Second row
        pos_y += WIDGET_LINE
        self.widgets["chord_label"] = Label(text="Chord", visible=False)
        self.widgets["chord"] = Label(text="Chord", visible=False)
        for fieldname in (
            "scale",
            "chord_type",
            "current_chord",
            "next_chord",
            "root_note",
        ):
            self.widgets["chord"].hook(
                self.model,
                fieldname,
                f"{fieldname}_to_chord",
                set_text=True,
                value_getter=lambda: self.model.chord_str,
            )
        self.widgets["chord"].on_click = lambda v, _b: (
            self.activate_widget("chord"),
            self.increment(),
        )
        self.make_row(
            [
                self.widgets[widget_name]
                for widget_name in (
                    "chord_label",
                    "chord",
                )
            ],
            pos_y=pos_y,
            width=rows_size,
        )

    def increment(self, *a, **kw):
        """
        Handle special cases.
        """
        if self.active_widget == "chord":
            self.model.toggle_chords_mode()
            return
        super().increment(*a, **kw)

    def midi_tick(self, ticks, playing):
        """
        Animate the metronome to show that clock is running.
        """
        metronome = self.widgets.get("metronome")
        if not metronome:
            return
        if ticks % (BEAT / 2) == 0:
            metro_label = ""
            counting = 0
            if ticks % BEAT == 0:
                counting = int((ticks % BAR) / BEAT) + 1
                metro_label = str(counting)
            if metro_label and not playing:
                metro_label = "."
            metronome.set_text(metro_label)
            if counting == 1 and playing:
                metronome.highlight()
            else:
                metronome.shade()
