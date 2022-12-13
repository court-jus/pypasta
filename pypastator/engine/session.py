import pygame.midi

from constants import FONT_SIZE, BASE_WIDGET_HEIGHT, WIDGETS_MARGIN, SCALES, CHORDS, SCALE_NAMES
from widgets.led import Led
from widgets.menu import Menu
from engine.track import Track
from engine.field import EnumField
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
        self.chord_progression = [1]
        self.current_chord = 0
        self.scale = EnumField(choices=SCALES)
        self.chord = EnumField(choices=CHORDS)
        self.tracks = {}
        self.playing = True
        self.cc_controls = {}
        self.menu_buttons = {}
        self.menu = Menu(self)

    @property
    def scale_str(self):
        return SCALE_NAMES[self.scale.value]


    @property
    def chord_str(self):
        scale_notes = SCALES[self.scale.value]
        chord_notes = CHORDS[self.chord.value]
        notes = []
        for degree in chord_notes:
            scale_degree = (degree - 1 + self.current_chord - 1) % len(scale_notes)
            note = scale_notes[scale_degree] + 12
            notes.append(note)
        return ", ".join(
            [pygame.midi.midi_to_ansi_note(note)[:-1] for note in notes]
        )

    def load(self, data):
        for loadable_key in ("scale_name", "chord_progression", "playing"):
            if loadable_key in data:
                setattr(self, loadable_key, data[loadable_key])
        for track_id, track in data.get("tracks", {}).items():
            track_id = int(track_id)
            self.add_track(track_id, track)
        self.toggle_menu(0)

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
        if relative_ticks % BAR == 0:
            self.current_chord = int(relative_ticks / BAR) % len(self.chord_progression)
        out_evts = []
        for track in self.tracks.values():
            out_evts.extend(
                track.midi_tick(
                    relative_ticks,
                    timestamp,
                    self.chord_progression[self.current_chord],
                )
            )
        return out_evts

    def handle_cc(self, cchannel, cc, value):
        if cchannel != 15:
            print(f"Ignored CC on channel {cchannel}, {cc}, {value}")
            return

        if cc < 8:
            self.menu.handle_cc(cc, value)
            return

        if cc >= 48 and cc <= 56 and value == 127:
            track_id = cc - 48
            if track_id in self.tracks:
                self.toggle_menu(track_id)
            else:
                self.add_track(track_id)
            return

        for track_id, track in self.tracks.items():
            track.handle_cc(cc, value)

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
            track.engine.pos = 0
