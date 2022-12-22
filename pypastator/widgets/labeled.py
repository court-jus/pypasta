"""
Utility class for wigets that can have a label next to them.
"""
from pypastator.constants import WIDGET_LABEL_SIZE, WIDGETS_MARGIN
from pypastator.widgets import BaseWidget
from pypastator.widgets.label import Label


class Labeled(BaseWidget):
    """
    A labeled widget can have a label displayed next to it.
    """

    def __init__(self, *a, **kw):
        self.label = None
        super().__init__(*a, **kw)

    def draw(self):
        """
        Draw this widget on a pygame surface.
        """
        if self.label is not None:
            self.label.draw()

    def widget_init(self, label=None):
        """
        Init code specific to this widget.
        """
        if label:
            self.label = Label(
                text=label,
                fcolor=self.fcolor,
                bcolor=self.bcolor,
                w=WIDGET_LABEL_SIZE,
                h=self.height,
                x=self.pos_x,
                y=self.pos_y,
                visible=self.visible,
            )
            self.pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN
            self.rect.centerx += WIDGET_LABEL_SIZE + WIDGETS_MARGIN

    def set_label(self, new_label):
        """
        Change this widget's label.
        """
        self.label.set_text(new_label)
        if self.visible:
            self.draw()

    def show(self):
        """
        Show this widget and its label.
        """
        if self.label is not None:
            self.label.show()
        super().show()

    def hide(self):
        """
        Hide this widget.
        """
        if self.label is not None:
            self.label.hide()
        super().hide()

    def highlight(self):
        """
        Highlight this widget.
        """
        if self.label is not None:
            self.label.set_value(True)

    def shade(self):
        """
        Remove highlighting from this widget.
        """
        if self.label is not None:
            self.label.set_value(False)
