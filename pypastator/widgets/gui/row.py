"""
Helper functions to build rows (and tables).
"""

from pypastator.constants import SCR_WIDTH, WIDGETS_MARGIN


def make_row(widgets, pos_x=0, pos_y=0, width=SCR_WIDTH, debug=False):
    """
    Make a row with given widgets.
    """
    total_width = sum(widget.get_width() for widget in widgets)
    guts = len(widgets) - 1
    guts_size = guts * WIDGETS_MARGIN
    widgets_size = (width - 2 * WIDGETS_MARGIN) - guts_size
    size_ratio = widgets_size / total_width
    current_x = pos_x + WIDGETS_MARGIN
    current_y = pos_y
    for widget in widgets:
        new_width = widget.get_width() * size_ratio
        if debug:
            print("w", widget, "o", widget.get_width(), "n", new_width)
        widget.move_to(current_x, current_y, new_width=new_width)
        current_x += new_width + WIDGETS_MARGIN
