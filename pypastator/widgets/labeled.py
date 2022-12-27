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
        super().draw()
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

    def get_width(self):
        """
        Get this widget's width.
        """
        width = super().get_width()
        if self.label is not None:
            width += WIDGETS_MARGIN + self.label.get_width()
        return width

    def move_to(self, new_x, new_y, new_width=None):
        """
        Move widget and its label to another position.
        """
        self.hide()
        self.pos_x = new_x
        self.pos_y = new_y
        if self.label is not None:
            self.label.move_to(self.pos_x, new_y)
            self.pos_x += self.label.width + WIDGETS_MARGIN
        if new_width is not None:
            self.width = new_width
            if self.label is not None:
                self.width -= self.label.width + WIDGETS_MARGIN
        self.apply_new_pos()

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
