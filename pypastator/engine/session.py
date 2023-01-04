"""
Session holds all the details for the current song.
"""
import json
import os
import sys

import pygame.midi
from faker import Faker
from slugify import slugify

from pypastator.constants import (
    BAR,
    CHORDS,
    MENU_CC_NEXT_PAGE,
    MENU_CC_PREV_PAGE,
    SCALE_NAMES,
    SCALES,
)
from pypastator.engine.field import EnumField, Field, ListField
from pypastator.engine.track import Track
from pypastator.engine.utils import int_to_roman
from pypastator.widgets.gui.base import WithMenu
from pypastator.widgets.gui.mouse import MouseGUI
from pypastator.widgets.gui.session import SessionGUI
from pypastator.widgets.gui.settings import SettingsGUI
from pypastator.widgets.message import Message

DEFAULT_TRACK = {
    "type": "arp",
    "pitch": 60,
    "gravity": 12,
    "rythm": 100,
    "pattern": 100,
    "basevel": 100,
    "midi_channel": 10,
    "active": False,
}

LOADABLE_KEYS = ("scale_name", "root_note", "chord_progression", "playing", "title")


class Session(WithMenu):
    """
    Definition of a Session.
    """

    def __init__(self, pasta):
        super().__init__()
        self.pasta = pasta
        self.scale_name = "major"
        self.root_note = 0
        self.chords_mode = "progression"
        self.chord_progression = ListField()
        self.chord_progression.set_value([1])
        self.progression_pos = 0
        self.next_chord = Field()
        self.title = ""
        self.scale = EnumField(choices=SCALES)
        self.scale.set_value(SCALE_NAMES.index(self.scale_name))
        self.chord_type = EnumField(choices=CHORDS)
        self.current_chord = ListField()
        self.current_chord.set_value(
            [
                degree_in_chord
                + self.chord_progression.get_value(self.progression_pos)
                - 1
                for degree_in_chord in self.chord_type.get_value()
            ]
        )
        self.tracks = {}
        self.selected_track = None
        self.playing = True
        self.mouse_menu = None
        self.cc_controls = {}
        if "pytest" not in sys.modules:
            self.message = Message()
            self.main_menu = SessionGUI(self, 300)
            self.main_menu.show()
            self.main_menu.activate_widget(self.main_menu.default_widget)
            self.mouse_menu = MouseGUI(self)
            self.settings_menu = SettingsGUI(self)

    @property
    def scale_str(self):
        """
        Get a str representation of the scale.
        """
        return (
            f"{pygame.midi.midi_to_ansi_note(self.root_note + 12)[:-1]}"
            f"{SCALE_NAMES[self.scale.value]}"
        )

    def get_scale_notes(self):
        """
        Get the notes in current scale.
        """
        return [
            self.root_note + note_in_scale for note_in_scale in self.scale.get_value()
        ]

    @property
    def chord_str(self):
        """
        Get a str representation of the chord.
        """
        scale_notes = self.get_scale_notes()
        chord_notes = [
            note_in_chord - 1 for note_in_chord in self.current_chord.get_value()
        ]
        notes = []
        for degree in chord_notes:
            scale_degree = degree % len(scale_notes)
            note = scale_notes[scale_degree] + 12
            notes.append(note)
        if self.chords_mode == "manual":
            chord_name = ", ".join(map(str, chord_notes))
        else:
            chord_name = int_to_roman(
                self.chord_progression.get_value(self.progression_pos)
            )

        result = f"[{chord_name}]: " + ", ".join(
            [pygame.midi.midi_to_ansi_note(note)[:-1] for note in notes]
        )
        if self.next_chord.get_value():
            next_chord_notes = [
                scale_notes[(degree_in_chord + self.next_chord.get_value() - 2) % len(scale_notes)]
                + 12
                for degree_in_chord in self.chord_type.get_value()
            ]
            result = result + " => " + (", ".join(
                [pygame.midi.midi_to_ansi_note(note)[:-1] for note in next_chord_notes]
            ))
        return result

    def new_song(self):
        """
        Clear current song.
        """
        self.stop()
        self.pasta.all_sound_off()
        for track in self.tracks.values():
            if track.engine.main_menu:
                track.engine.main_menu.hide()
            for menu in track.engine.sub_menus:
                menu.hide()
        self.tracks = {}
        self.selected_track = None
        self.current_chord.set_value([], force=True)
        self.chord_progression.set_value([1], force=True)
        self.progression_pos = 0
        self.next_chord.set_value(0, force=True)
        self.title = self.get_title(generate_new=True)
        self.scale_name = "major"
        self.root_note = 0
        self.chords_mode = "progression"

    def load(self, filename):
        """
        Load Session from data.
        """
        self.new_song()
        data = {}
        with open(os.path.join("songs", filename), "r", encoding="utf8") as file_pointer:
            data = json.load(file_pointer)
        for loadable_key in LOADABLE_KEYS:
            if loadable_key in data:
                field = getattr(self, loadable_key)
                if isinstance(field, Field):
                    field.set_value(data[loadable_key])
                else:
                    setattr(self, loadable_key, data[loadable_key])
        for track_id, track in data.get("tracks", {}).items():
            track_id = int(track_id)
            self.add_track(track_id, track)
        self.scale.set_value(SCALE_NAMES.index(self.scale_name))
        self.current_chord.set_value(
            [
                degree_in_chord
                + self.chord_progression.get_value(self.progression_pos)
                - 1
                for degree_in_chord in self.chord_type.get_value()
            ]
        )

    def save(self):
        """
        Save Session to a JSON file.

        If the session has no name, generate a random title.
        """
        data = {
            "tracks": {
                track.track_id: track.engine.save() for track in self.tracks.values()
            },
            "title": self.get_title(),
        }
        for loadable_key in LOADABLE_KEYS:
            field = getattr(self, loadable_key)
            if isinstance(field, Field):
                data.update({loadable_key: field.get_value()})
            else:
                data.update({loadable_key: field})

        filename = slugify(data["title"]) + ".json"
        with open(
            os.path.join("songs", filename), "w", encoding="utf8"
        ) as file_pointer:
            json.dump(data, file_pointer, indent=2)
        self.message.say(f"Song [{data['title']}] saved as [{filename}]")

    def get_title(self, generate_new=False):
        """
        Get current title or generate a new one.
        """
        if generate_new or not self.title:
            fake = Faker()
            self.set_title(fake.catch_phrase())
        return self.title

    def set_title(self, value):
        """
        Set title.
        """
        self.title = value

    def add_track(self, track_id=None, data=None):
        """
        Add a new track to the session.
        """
        new_track_id = track_id if track_id is not None else len(self.tracks.keys())
        track_data = data if data is not None else DEFAULT_TRACK
        track = Track(new_track_id, self)
        track.load(track_data)
        self.tracks[new_track_id] = track
        self.message.say(f"Track [{new_track_id}] added")
        self.select_track(new_track_id)

    def select_track(self, track_id):
        """
        Select this track for modification.

        TODO: maybe use a Field instead of setting the widget value directly.
        """
        if self.selected_track is not None:
            cur_track = self.tracks[self.selected_track]
            cur_track.hide_all_menus()
            if cur_track.engine is not None:
                cur_track.engine.hide_all_menus()
            cur_track.engine.main_menu.widgets["menu"].set_value(False)
        self.selected_track = track_id
        sel_track = self.tracks[self.selected_track]
        sel_track.engine.main_menu.widgets["menu"].set_value(True)
        self.deactivate_active_menu()
        sel_track.engine.next_page()

    def next_page(self, go_back=False):
        """
        Activate next page.

        Skipped if settings menu is visible.
        While going down, we scroll through each page.
        While going up, go directly from section to section.
        """
        if self.settings_menu is not None and self.settings_menu.any_visible():
            return
        session_active = self.get_active_menu()
        track_active = None
        engine_active = None
        cur_track = None
        cur_engine = None
        if self.selected_track is not None:
            cur_track = self.tracks[self.selected_track]
            track_active = cur_track.get_active_menu()
            cur_engine = cur_track.engine
            if cur_engine is not None:
                engine_active = cur_track.engine.get_active_menu()
        res = False
        if session_active is not False or (
            engine_active is not None and not isinstance(engine_active, bool)
        ):
            self.deactivate_active_menu()
            res = cur_engine.next_page(go_back)
        if res is False:
            if track_active:
                cur_track.deactivate_active_menu()
            if cur_engine:
                cur_engine.deactivate_active_menu()
            self.main_menu.show()
            self.main_menu.activate_widget(self.main_menu.default_widget)

    def toggle_chords_mode(self):
        """
        Switch chords mode.

        In manual mode, the user plays chords with 'menu' buttons.
        In progression mode, the song's chord progression is followed.
        """
        self.chords_mode = {
            "progression": "manual",
            "manual": "progression",
        }[self.chords_mode]
        self.message.say(f"[{self.chords_mode}] chords mode")
        if self.chords_mode == "manual":
            for track in self.tracks.values():
                if track.engine and track.engine.main_menu is not None:
                    track.engine.main_menu.widgets["menu"].hide()
        else:
            for track in self.tracks.values():
                if track.engine and track.engine.main_menu is not None:
                    track.engine.main_menu.widgets["menu"].show()

    def midi_tick(self, ticks, timestamp):
        """
        Handle Midi tick event.
        """
        if not self.playing:
            return []
        relative_ticks = ticks - self.playing
        if relative_ticks % BAR == 0:
            if self.next_chord.get_value():
                self.current_chord.set_value(
                    [
                        degree_in_chord
                        + self.next_chord.get_value()
                        - 1
                        for degree_in_chord in self.chord_type.get_value()
                    ]
                )
                self.next_chord.set_value(0, force=True)
            elif self.chords_mode == "progression":
                self.progression_pos = int(relative_ticks / BAR) % len(
                    self.chord_progression.get_value()
                )
                self.current_chord.set_value(
                    [
                        degree_in_chord
                        + self.chord_progression.get_value(self.progression_pos)
                        - 1
                        for degree_in_chord in self.chord_type.get_value()
                    ]
                )
        out_evts = []
        for track in self.tracks.values():
            out_evts.extend(
                track.midi_tick(
                    relative_ticks,
                    timestamp,
                    self.chord_progression.get_value(self.progression_pos),
                )
            )
        return out_evts

    def handle_tick(self):
        """
        Method called every event loop.
        """
        if self.settings_menu is not None and self.settings_menu.any_visible():
            self.settings_menu.handle_tick()
        else:
            super().handle_tick()
            for track in self.tracks.values():
                track.handle_tick()
            if self.message is not None:
                self.message.handle_tick()
            if self.mouse_menu is not None:
                self.mouse_menu.handle_tick()

    def _handle_global_cc(self, cc_number, value):
        """
        Handle Midi CC events that are not related to tracks.
        """
        if value != 127:
            return

        if cc_number == 7:
            if self.settings_menu is not None and not self.settings_menu.any_visible():
                self.settings_menu.show()
                self.settings_menu.activate_next()
        elif self.chords_mode == "progression":
            self._handle_menu_cc(cc_number)
        elif self.chords_mode == "manual":
            self._handle_chords_cc(cc_number)

    def _handle_menu_cc(self, cc_number):
        """
        Handle menu navigation via CC events.
        """
        if 48 <= cc_number < 56:
            track_id = cc_number - 48
            if track_id not in self.tracks:
                self.add_track(track_id)

    def _handle_chords_cc(self, cc_number):
        """
        Handle choosing chord via CC.
        """
        if 48 <= cc_number < 56:
            self.next_chord.set_value(cc_number - 48 + 1, force=True)

    def handle_cc(self, cc_channel, cc_number, cc_value):
        """
        Handle Midi CC event.

        Bypassed if settings menu is visible.
        """
        if self.settings_menu is not None and self.settings_menu.any_visible():
            self.settings_menu.handle_cc(cc_channel, cc_number, cc_value)
            return
        super().handle_cc(cc_channel, cc_number, cc_value)
        for track in self.tracks.values():
            track.handle_cc(cc_channel, cc_number, cc_value)
        if cc_channel != 15:
            print(f"Ignored CC on channel {cc_channel}, {cc_number}, {cc_value}")
            return

        if cc_value == 127:
            if cc_number == MENU_CC_NEXT_PAGE:
                self.next_page()
            elif cc_number == MENU_CC_PREV_PAGE:
                self.next_page(go_back=True)

        self._handle_global_cc(cc_number, cc_value)

    def handle_click(self, pos, button):
        """
        Handle click event based on its position.
        """
        super().handle_click(pos, button)
        for track in self.tracks.values():
            track.handle_click(pos, button)
        if self.mouse_menu is not None:
            self.mouse_menu.handle_click(pos, button)
        if self.settings_menu is not None:
            self.settings_menu.handle_click(pos, button)

    def handle_mouse_move(self, _pos):
        """
        Handle mouse moves.
        """
        if self.mouse_menu is not None:
            self.mouse_menu.show()

    def stop(self):
        """
        Stop playing and reset play position for all the tracks.
        """
        self.playing = False
        for track in self.tracks.values():
            track.engine.reset_pos()
