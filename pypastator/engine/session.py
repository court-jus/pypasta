"""
Session holds all the details for the current song.
"""
import json

import pygame.midi
from faker import Faker
from slugify import slugify

from pypastator.constants import (
    BAR,
    BASE_WIDGET_HEIGHT,
    CHORDS,
    SCALE_NAMES,
    SCALES,
    WIDGETS_MARGIN,
)
from pypastator.engine.field import EnumField, Field, ListField
from pypastator.engine.track import Track
from pypastator.engine.utils import int_to_roman
from pypastator.widgets.led import Led
from pypastator.widgets.menu import Menu
from pypastator.widgets.message import Message

DEFAULT_TRACK = {
    "type": "arp",
    "pitch": 40,
    "rythm": 100,
    "pattern": 100,
    "basevel": 100,
    "midi_channel": 10,
    "active": False,
}

LOADABLE_KEYS = ("scale_name", "root_note", "chord_progression", "playing", "title")


class Session:
    """
    Definition of a Session.
    """

    def __init__(self, pasta):
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
        self.playing = True
        self.cc_mode = "menu"
        self.cc_controls = {}
        self.menu_buttons = {}
        self.message = Message()
        self.menu = Menu(self)

    @property
    def scale_str(self):
        """
        Get a str representation of the scale.
        """
        return f"{pygame.midi.midi_to_ansi_note(self.root_note + 12)[:-1]} {SCALE_NAMES[self.scale.value]}"

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
        topy = WIDGETS_MARGIN + (BASE_WIDGET_HEIGHT + WIDGETS_MARGIN) * track_id
        self.menu_buttons[track_id] = Led(
            y=topy,
            value=False,
            emoji="⚙️",
            on_click=lambda v: self.toggle_menu(track_id),
        )
        self.message.say(f"Track [{track_id}] added")

    def midi_tick(self, ticks, timestamp):
        """
        Handle Midi tick event.
        """
        self.message.midi_tick(ticks, timestamp)
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

    def _handle_track_cc(self, cc_number, value):
        """
        Pass Midi CC event to tracks.
        """
        for track in self.tracks.values():
            track.handle_cc(cc_number, value)

    def _handle_global_cc(self, cc_number, value):
        """
        Handle Midi CC events that are not related to tracks.
        """
        if value != 127:
            return

        # Switch buttons "mode"
        if 4 <= cc_number < 8:
            if cc_number == 4:
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
        if cc_number < 4:
            self.menu.handle_cc(cc_number)
        elif 48 <= cc_number < 56:
            track_id = cc_number - 48
            if track_id in self.tracks:
                self.toggle_menu(track_id)
            else:
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

    def handle_cc(self, cchannel, cc_number, value):
        """
        Handle Midi CC event.
        """
        if cchannel != 15:
            print(f"Ignored CC on channel {cchannel}, {cc_number}, {value}")
            return

        if 8 <= cc_number < 48:
            self._handle_track_cc(cc_number, value)
        else:
            self._handle_global_cc(cc_number, value)

    def toggle_menu(self, track_id):
        """
        Hide/Show menu for a specific track.

        If menu is already shown for said track, activate its next widget.
        """
        if self.menu.visible and self.menu.current_track.track_id == track_id:
            next_widget_activated = self.menu.activate_next()
            if not next_widget_activated:
                self.menu_buttons[self.menu.current_track.track_id].set_value(False)
                self.menu.hide()
        elif self.menu.visible:
            self.menu_buttons[self.menu.current_track.track_id].set_value(False)
            self.menu.hide()
            self.menu.show(self.tracks[track_id])
            self.menu_buttons[self.menu.current_track.track_id].set_value(True)
        else:
            self.menu.show(self.tracks[track_id])
            self.menu_buttons[self.menu.current_track.track_id].set_value(True)

    def handle_click(self, pos):
        """
        Handle click event based on its position.
        """
        for track in self.tracks.values():
            track.handle_click(pos)
        for menu_button in self.menu_buttons.values():
            menu_button.handle_click(pos)
        self.menu.handle_click(pos)

    def stop(self):
        """
        Stop playing and reset play position for all the tracks.
        """
        self.playing = False
        for track in self.tracks.values():
            track.engine.pos.set_value(0)
