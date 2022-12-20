import pygame.midi

from constants import (
    FONT_SIZE,
    BASE_WIDGET_HEIGHT,
    WIDGETS_MARGIN,
    SCALES,
    CHORDS,
    SCALE_NAMES,
)
from widgets.led import Led
from widgets.menu import Menu
from engine.track import Track
from engine.field import EnumField, ListField
from constants import BAR


DEFAULT_TRACK = {
    "type": "arp",
    "pitch": 40,
    "rythm": 100,
    "pattern": 100,
    "basevel": 100,
    "midi_channel": 10,
    "active": False,
}


class Session:
    def __init__(self, pasta):
        self.pasta = pasta
        self.scale_name = "major"
        self.chords_mode = "manual"
        self.chord_progression = [1]
        self.progression_pos = 0
        self.scale = EnumField(choices=SCALES)
        self.chord_type = EnumField(choices=CHORDS)
        self.current_chord = ListField()
        self.current_chord.set_value(
            [
                degree_in_chord + self.chord_progression[self.progression_pos] - 1
                for degree_in_chord in self.chord_type.get_value()
            ]
        )
        self.tracks = {}
        self.playing = True
        self.cc_mode = "menu"
        self.cc_controls = {}
        self.menu_buttons = {}
        self.menu = Menu(self)

    @property
    def scale_str(self):
        return SCALE_NAMES[self.scale.value]

    @property
    def chord_str(self):
        scale_notes = SCALES[self.scale.value]
        chord_notes = CHORDS[self.chord_type.value]
        notes = []
        for degree in chord_notes:
            scale_degree = (degree - 1 + self.progression_pos - 1) % len(scale_notes)
            note = scale_notes[scale_degree] + 12
            notes.append(note)
        return ", ".join([pygame.midi.midi_to_ansi_note(note)[:-1] for note in notes])

    def load(self, data):
        for loadable_key in ("scale_name", "chord_progression", "playing"):
            if loadable_key in data:
                setattr(self, loadable_key, data[loadable_key])
        for track_id, track in data.get("tracks", {}).items():
            track_id = int(track_id)
            self.add_track(track_id, track)
        self.current_chord.set_value(
            [
                degree_in_chord + self.chord_progression[self.progression_pos] - 1
                for degree_in_chord in self.chord_type.get_value()
            ]
        )

    def add_track(self, track_id, data=DEFAULT_TRACK):
        t = Track(track_id, self)
        t.load(data)
        self.tracks[track_id] = t
        y = WIDGETS_MARGIN + (BASE_WIDGET_HEIGHT + WIDGETS_MARGIN) * track_id
        self.menu_buttons[track_id] = [
            Led(y=y, value=False, emoji="⚙️"),
            lambda _: self.toggle_menu(track_id),
        ]

    def midi_tick(self, ticks, timestamp):
        if not self.playing:
            return []
        relative_ticks = ticks - self.playing
        if relative_ticks % BAR == 0 and self.chords_mode != "manual":
            self.progression_pos = int(relative_ticks / BAR) % len(
                self.chord_progression
            )
            self.current_chord.set_value(
                [
                    degree_in_chord + self.chord_progression[self.progression_pos] - 1
                    for degree_in_chord in self.chord_type.get_value()
                ]
            )
        out_evts = []
        for track in self.tracks.values():
            out_evts.extend(
                track.midi_tick(
                    relative_ticks,
                    timestamp,
                    self.chord_progression[self.progression_pos],
                )
            )
        return out_evts

    def handle_cc(self, cchannel, cc, value):
        if cchannel != 15:
            print(f"Ignored CC on channel {cchannel}, {cc}, {value}")
            return

        if cc >= 8 and cc < 48:
            for track_id, track in self.tracks.items():
                track.handle_cc(cc, value)
            return

        if value != 127:
            return

        if cc >= 4 and cc < 8:
            if cc == 4:
                self.cc_mode = "menu"
            elif cc == 5:
                self.cc_mode = "chords"
            return

        if self.cc_mode == "menu":
            if cc < 4:
                self.menu.handle_cc(cc, value)
            elif cc >= 48 and cc < 56:
                track_id = cc - 48
                if track_id in self.tracks:
                    self.toggle_menu(track_id)
                else:
                    self.add_track(track_id)
            return

        if self.cc_mode == "chords":
            if cc >= 48 and cc < 56:
                self.current_chord.set_value(
                    [
                        degree_in_chord + cc - 48
                        for degree_in_chord in self.chord_type.get_value()
                    ]
                )

    def toggle_menu(self, track_id):
        if self.menu.visible:
            self.menu_buttons[self.menu.current_track.track_id][0].set_value(False)
        if self.menu.visible and self.menu.current_track.track_id == track_id:
            self.menu.hide()
        else:
            self.menu.hide()
            self.menu.show(self.tracks[track_id])
            self.menu_buttons[self.menu.current_track.track_id][0].set_value(True)

    def handle_click(self, pos):
        for track in self.tracks.values():
            track.handle_click(pos)
        for menu_button in self.menu_buttons.values():
            menu_button[0].handle_click(pos, menu_button[1])
        self.menu.handle_click(pos)

    def stop(self):
        self.playing = False
        for track in self.tracks.values():
            track.engine.pos.set_value(0)
