"""
Helper functions to build rows (and tables).
"""

from pypastator.constants import WIDGETS_MARGIN


def make_row(widgets, pos_x, pos_y, width=1024 - 2 * WIDGETS_MARGIN, debug=False):
    """
    Make a row with given widgets.
    """
    total_width = sum(widget.get_width() for widget in widgets)
    guts = len(widgets) - 1
    guts_size = guts * WIDGETS_MARGIN
    widgets_size = width - guts_size
    size_ratio = widgets_size / total_width
    current_x = pos_x
    current_y = pos_y
    for widget in widgets:
        new_width = widget.get_width() * size_ratio
        if debug:
            print("w", widget, "o", widget.get_width(), "n", new_width)
        widget.move_to(current_x, current_y, new_width=new_width)
        current_x += new_width + WIDGETS_MARGIN
