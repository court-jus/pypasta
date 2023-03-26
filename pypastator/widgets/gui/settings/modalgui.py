"""
Helper for settings GUI.
"""
import pygame.display

from pypastator.constants import (
    BLACK,
    DARKEST_GRAY,
    MOUSE_RIGHT_CLICK,
    SCR_HEIGHT,
    SCR_WIDTH,
    WHITE,
)
from pypastator.widgets.gui.base import GUI

MODAL_MARGIN = 20
MODAL_BORDER = 3
TOTAL_MODAL_MARGIN = MODAL_MARGIN + MODAL_BORDER
MODAL_ROW_WIDTH = SCR_WIDTH - (TOTAL_MODAL_MARGIN * 2)


class ModalGUI(GUI):
    """
    A GUI that's displayed over the rest.
    """

    def __init__(self, *a, **kw):
        self.is_main_settings_gui = False
        self.sub_menus = {}
        super().__init__(*a, **kw)

    def redraw(self):
        surf = pygame.display.get_surface()
        surf.fill(
            WHITE,
            (
                MODAL_MARGIN,
                MODAL_MARGIN,
                SCR_WIDTH - (MODAL_MARGIN * 2),
                SCR_HEIGHT - (MODAL_MARGIN * 2),
            ),
        )
        surf.fill(
            DARKEST_GRAY,
            (
                TOTAL_MODAL_MARGIN,
                TOTAL_MODAL_MARGIN,
                SCR_WIDTH - ((TOTAL_MODAL_MARGIN) * 2),
                SCR_HEIGHT - ((TOTAL_MODAL_MARGIN) * 2),
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
        rect = pygame.Rect(0, 0, SCR_WIDTH, SCR_HEIGHT)
        surf.fill(BLACK, rect)
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
