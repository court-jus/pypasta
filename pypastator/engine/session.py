"""
Session holds all the details for the current song.
"""
import json
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
from pypastator.widgets.gui.session import SessionGUI
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
        self.cc_mode = "menu"
        self.cc_controls = {}
        if "pytest" not in sys.modules:
            self.message = Message()
            self.main_menu = SessionGUI(self, 300)
            self.main_menu.show()
            self.main_menu.activate_widget(self.main_menu.default_widget)

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
        if self.chords_mode == "progression":
            chord_name = int_to_roman(
                self.chord_progression.get_value(self.progression_pos)
            )
        else:
            chord_name = ", ".join(map(str, chord_notes))
        return f"[{chord_name}]: " + ", ".join(
            [pygame.midi.midi_to_ansi_note(note)[:-1] for note in notes]
        )

    def load(self, data):
        """
        Load Session from data.
        """
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
        fake = Faker()
        data = {
            "tracks": {
                track.track_id: track.engine.save() for track in self.tracks.values()
            }
        }
        for loadable_key in LOADABLE_KEYS:
            field = getattr(self, loadable_key)
            if isinstance(field, Field):
                data.update({loadable_key: field.get_value()})
            else:
                data.update({loadable_key: field})

        track_name = self.title
        if not track_name:
            track_name = fake.catch_phrase()
            data["title"] = track_name
        filename = slugify(track_name) + ".json"
        with open(filename, "w", encoding="utf8") as file_pointer:
            json.dump(data, file_pointer, indent=2)
        self.message.say(f"Song [{track_name}] saved as [{filename}]")

    def add_track(self, track_id, data=None):
        """
        Add a new track to the session.
        """
        track_data = data if data is not None else DEFAULT_TRACK
        track = Track(track_id, self)
        track.load(track_data)
        self.tracks[track_id] = track
        self.message.say(f"Track [{track_id}] added")
        self.select_track(track_id)

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
        sel_track.engine.next_page()

    def next_page(self, go_back=False):
        """
        Activate next page.

        While going down, we scroll through each page.
        While going up, go directly from section to section.
        """
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

    def midi_tick(self, ticks, timestamp):
        """
        Handle Midi tick event.
        """
        self.message.midi_tick(timestamp)
        if not self.playing:
            return []
        relative_ticks = ticks - self.playing
        if relative_ticks % BAR == 0 and self.chords_mode == "progression":
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

    def _handle_global_cc(self, cc_number, value):
        """
        Handle Midi CC events that are not related to tracks.
        """
        if value != 127:
            return

        # Switch buttons "mode"
        if cc_number == 6:
            self.cc_mode = "menu"
            self.message.say("[Menu] mode")
            self.chords_mode = "progression"
        elif cc_number == 5:
            self.cc_mode = "chords"
            self.message.say("[Chords] mode")
            self.chords_mode = "manual"
        elif cc_number == 7:
            self.save()
        elif self.cc_mode == "menu":
            self._handle_menu_cc(cc_number)
        elif self.cc_mode == "chords":
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
            self.current_chord.set_value(
                [
                    degree_in_chord + cc_number - 48
                    for degree_in_chord in self.chord_type.get_value()
                ]
            )

    def handle_cc(self, cc_channel, cc_number, cc_value):
        """
        Handle Midi CC event.
        """
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

    def handle_click(self, pos):
        """
        Handle click event based on its position.
        """
        super().handle_click(pos)
        for track in self.tracks.values():
            track.handle_click(pos)

    def stop(self):
        """
        Stop playing and reset play position for all the tracks.
        """
        self.playing = False
        for track in self.tracks.values():
            track.engine.pos.set_value(0)
