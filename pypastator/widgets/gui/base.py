"""
Base class for all GUI menus.
"""

from collections import OrderedDict

from pypastator.constants import (
    MENU_CC_CHANNEL,
    MENU_CC_DECR,
    MENU_CC_INCR,
    MENU_CC_NEXT_WIDGET,
)
from pypastator.engine.field import Field


class GUI:
    """
    A GUI contains widgets hooked to a specific "model" (instance with 'Field' instances).
    """

    def __init__(self, model=None, pos_y=0):
        self.model = model
        self.visible = False
        self.widgets = OrderedDict()
        self.default_widget = None
        self.active_widget = None
        self.activable_widgets = []
        self.hideable = True
        self.init_widgets(pos_y)
        if not self.hideable:
            self.show()

    def init_widgets(self):
        """
        Initialize GUI's widgets.
        """
        raise NotImplementedError

    def hide(self):
        """
        Hide the GUI and its widgets.
        """
        for widget in self.widgets.values():
            widget.shade()
            widget.hide()
        self.active_widget = None
        self.visible = False

    def close(self):
        """
        Hide the GUI and unhook its widgets.
        """
        for widget in self.widgets.values():
            widget.hide()
            widget.unhook()
        self.visible = False

    def show(self):
        """
        Show the GUI and hook widgets.
        """
        if self.model is None:
            return
        for widget in self.widgets.values():
            widget.show()
        self.visible = True

    def activate_widget(self, widget_id):
        """
        Activate a widget for arrows manipulation.
        """
        if not self.visible:
            return
        if self.active_widget is not None:
            self.widgets[self.active_widget].shade()
        if widget_id is not None:
            self.widgets[widget_id].highlight()
        self.active_widget = widget_id

    def activate_next(self):
        """
        Activate next widget in order.
        """
        if not self.visible:
            self.show()
        current_pos = (
            self.activable_widgets.index(self.active_widget)
            if self.active_widget in self.activable_widgets
            else None
        )
        next_pos = None
        if self.activable_widgets:
            next_pos = 0 if current_pos is None else current_pos + 1
        if next_pos == len(self.activable_widgets):
            next_pos = 0
        if next_pos is not None:
            self.activate_widget(self.activable_widgets[next_pos])

    def increment(self, increment=1):
        """
        Increment/decrement the value behind the currently active widget.
        """
        if not self.visible:
            return
        print("Widget increment", self.active_widget, "on", self.model)
        if self.active_widget is None or self.model is None:
            return
        field = getattr(self.model, self.active_widget)
        print("  Field is", field)
        if isinstance(field, Field):
            field.increment(increment)

    def handle_click(self, pos):
        """
        Handle click events.
        """
        if not self.visible:
            return
        for widget in self.widgets.values():
            widget.handle_click(pos)

    def handle_cc(self, cc_channel, cc_number, cc_value):
        """
        Handle Midi CC events.
        """
        if (
            not self.visible
            or self.active_widget is None
            or cc_channel != MENU_CC_CHANNEL
            or cc_value != 127
        ):
            return
        if cc_number == MENU_CC_NEXT_WIDGET:
            self.activate_next()
        elif cc_number == MENU_CC_INCR:
            self.increment()
        elif cc_number == MENU_CC_DECR:
            self.increment(-1)


class WithMenu:
    """
    Utility class for models that can be attached to menus.
    """

    def __init__(self):
        self.main_menu = None
        self.sub_menus = []

    def close(self):
        """
        Unhook and hide all menus.
        """
        if self.main_menu is not None:
            self.main_menu.close()
        for menu in self.sub_menus:
            menu.close()

    def handle_click(self, pos):
        """
        Pass click event to this track's widgets.
        """
        if self.main_menu is not None:
            self.main_menu.handle_click(pos)
        for menu in self.sub_menus:
            menu.handle_click(pos)

    def handle_cc(self, cc_channel, cc_number, cc_value):
        """
        Handle Midi CC events.
        """
        # Filter out unneeded events
        if cc_channel != MENU_CC_CHANNEL:
            return
        if self.main_menu is None and not self.sub_menus:
            return

        # Forward CC to visible menus (main and sub)
        if self.main_menu is not None:
            self.main_menu.handle_cc(cc_channel, cc_number, cc_value)
        visible_menu = self.get_visible_menu()
        if visible_menu is not None:
            self.sub_menus[visible_menu].handle_cc(cc_channel, cc_number, cc_value)

    def get_visible_menu(self):
        """
        Get the menu that is currently visible.
        """
        visible_menus = [menu.visible for menu in self.sub_menus]
        if not any(visible_menus):
            return None
        return visible_menus.index(True)

    def get_active_menu(self):
        """
        Get the menu that currently has an active widget.

        returns:
          - True if main menu is active
          - Menu index if a submenu is active
          - False
        """
        main_is_active = (
            self.main_menu.active_widget is not None
            if self.main_menu is not None
            else None
        )
        if main_is_active:
            return True
        active_menus = [
            menu.visible and menu.active_widget is not None for menu in self.sub_menus
        ]
        if any(active_menus):
            return active_menus.index(True)
        return False

    def deactivate_active_menu(self):
        """
        Deactivate any active menu.
        """
        active_menu = self.get_active_menu()
        if active_menu is True:
            self.main_menu.activate_widget(None)
        elif not isinstance(active_menu, bool):
            self.sub_menus[active_menu].activate_widget(None)
