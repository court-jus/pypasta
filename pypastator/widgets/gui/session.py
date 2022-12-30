"""
GUIs for the Session model.
"""
from pypastator.constants import BIG_LABEL_W, WIDGET_LINE, WIDGETS_MARGIN
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
        self.default_widget = "scale"
        self.activable_widgets = ["scale", "chord"]

    def init_widgets(self):
        """
        Initialize GUI's widgets.
        """
        pos_y = self.pos_y
        self.hideable = False
        self.widgets["separator"] = Separator(y=pos_y, visible=False)
        pos_y += WIDGETS_MARGIN
        self.widgets["scale_label"] = Label(text="Scale", visible=False)
        self.widgets["scale"] = Label(text="", w=BIG_LABEL_W, visible=False)
        self.widgets["scale"].hook(
            self.model,
            "scale",
            "menu",
            set_text=True,
            value_getter=lambda: self.model.scale_str,
        )
        self.widgets["scale"].on_click = (
            # TODO: handle different buttons
            lambda v, _b: self.model.scale.increment()
            if v == 127
            else None
        )
        make_row(
            [
                self.widgets[widget_name]
                for widget_name in (
                    "scale_label",
                    "scale",
                )
            ],
            pos_y=pos_y,
        )
        # Second row
        pos_y += WIDGET_LINE
        self.widgets["chord_label"] = Label(text="Chord", visible=False)
        self.widgets["chord"] = Label(text="Chord", w=BIG_LABEL_W, visible=False)
        self.widgets["chord"].hook(
            self.model,
            "scale",
            "scale_to_chord",
            set_text=True,
            value_getter=lambda: self.model.chord_str,
        )
        self.widgets["chord"].hook(
            self.model,
            "chord_type",
            "chord_to_chord",
            set_text=True,
            value_getter=lambda: self.model.chord_str,
        )
        self.widgets["chord"].hook(
            self.model,
            "current_chord",
            "current_chord_to_chord",
            set_text=True,
            value_getter=lambda: self.model.chord_str,
        )
        # TODO: handle different buttons
        # TODO: how to activate chord mode with CC
        # lambda v, _b: ACTIVATE CHORD MODE
        self.widgets["chord"].on_click = None
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
