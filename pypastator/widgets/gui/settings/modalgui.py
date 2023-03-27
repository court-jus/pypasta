"""
Helper for settings GUI.
"""
import pygame.display

from pypastator.constants import BLACK, DARKEST_GRAY, MOUSE_RIGHT_CLICK, WHITE
from pypastator.widgets.gui.base import GUI

MODAL_BORDER = 3
MODAL_WIDTH = 984
MODAL_HEIGHT = 728


class ModalGUI(GUI):
    """
    A GUI that's displayed over the rest.
    """

    def __init__(self, *a, **kw):
        self.is_main_settings_gui = False
        self.sub_menus = {}
        super().__init__(*a, **kw)

    def get_base_xy(self):
        """
        Return the top-left corner inside the modal.
        """
        window_width, window_height = pygame.display.get_window_size()
        return (
            (window_width - MODAL_WIDTH) / 2 + MODAL_BORDER,
            (window_height - MODAL_HEIGHT) / 2 + MODAL_BORDER,
        )

    def get_row_width(self):
        """
        Return the internal width of the modal.
        """
        return MODAL_WIDTH - 2 * MODAL_BORDER

    def redraw(self):
        surf = pygame.display.get_surface()
        pos_x, pos_y = self.get_base_xy()
        surf.fill(
            WHITE,
            (
                pos_x - MODAL_BORDER,
                pos_y - MODAL_BORDER,
                MODAL_WIDTH,
                MODAL_HEIGHT,
            ),
        )
        surf.fill(
            DARKEST_GRAY,
            (
                pos_x,
                pos_y,
                MODAL_WIDTH - 2 * MODAL_BORDER,
                MODAL_HEIGHT - 2 * MODAL_BORDER,
            ),
        )
        super().redraw()

    def init_widgets(self):
        pass

    def any_visible(self):
        """
        True if self is visible or any of its submenus.
        """
        return self.visible or any(sub.visible for sub in self.sub_menus.values())

    def update_widgets(self):
        """
        Should be implemented by sub-classes.
        """
        raise NotImplementedError

    def show(self):
        """
        Show this GUI hide its submenus.
        """
        for submenu in self.sub_menus.values():
            if submenu.visible:
                submenu.hide()
        if self.visible:
            return
        super().show()
        self.update_widgets()

    def handle_click(self, pos, button):
        if self.visible:
            if button == MOUSE_RIGHT_CLICK:
                self.hide()
            else:
                super().handle_click(pos, button)
        else:
            for submenu in self.sub_menus.values():
                submenu.handle_click(pos, button)

    def handle_tick(self, *a, **kw):
        if self.visible:
            super().handle_tick(*a, **kw)
        else:
            for submenu in self.sub_menus.values():
                submenu.handle_tick(*a, **kw)

    def handle_cc(self, cc_channel, cc_number, cc_value):
        if cc_value != 127:
            return
        if cc_number == 7:
            if self.visible:
                self.hide()
        if self.visible:
            super().handle_cc(cc_channel, cc_number, cc_value)
        else:
            for submenu in self.sub_menus.values():
                submenu.handle_cc(cc_channel, cc_number, cc_value)

    def hide(self):
        for submenu in self.sub_menus.values():
            submenu.hide()
        if not self.visible:
            return
        # Shade the whole UI
        surf = pygame.display.get_surface()
        pos_x, pos_y = self.get_base_xy()
        surf.fill(
            BLACK,
            (
                pos_x - MODAL_BORDER,
                pos_y - MODAL_BORDER,
                MODAL_WIDTH,
                MODAL_HEIGHT,
            ),
        )
        super().hide()
        if not self.is_main_settings_gui:
            self.model.settings_menu.show()
            self.model.settings_menu.activate_next()

    def show_submenu(self, submenu):
        """
        Hide this menu and show said submenu.
        """
        self.hide()
        self.sub_menus[submenu].show()
        self.sub_menus[submenu].activate_next()
