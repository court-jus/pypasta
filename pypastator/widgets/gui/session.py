"""
GUIs for the Session model.
"""
from pypastator.constants import WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.base import GUI
from pypastator.widgets.gui.row import make_row
from pypastator.widgets.label import Label
from pypastator.widgets.separator import Separator


class SessionGUI(GUI):
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
        self.hideable = False
        self.widgets["separator"] = Separator(pos_y=pos_y, visible=False)
        pos_y += WIDGETS_MARGIN
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
        make_row(
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
        make_row(
            [
                self.widgets[widget_name]
                for widget_name in (
                    "chord_label",
                    "chord",
                )
            ],
            pos_y=pos_y,
        )

    def increment(self, *a, **kw):
        """
        Handle special cases.
        """
        if self.active_widget == "chord":
            self.model.toggle_chords_mode()
            return
        super().increment(*a, **kw)
