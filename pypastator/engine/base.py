"""
Base for all musical engines.
"""
import sys

import pygame.midi

from pypastator.constants import (
    ACCENT,
    NOTE_PATTERNS,
    PONCTUATION_NOT,
    PONCTUATION_PART,
    PONCTUATION_START,
    RYTHM_PATTERNS,
    WIDGET_LINE,
    WIDGETS_MARGIN,
)
from pypastator.engine.field import BooleanField, EnumField, Field
from pypastator.engine.lfo import LFO
from pypastator.engine.utils import spread_notes
from pypastator.widgets.gui.base import WithMenu
from pypastator.widgets.gui.engine import LFOGUI, EngineDetailsGUI, MainEngineGUI

LOADABLE_KEYS = (
    "pitch",
    "gravity",
    "rythm",
    "pattern",
    "basevel",
    "midi_channel",
    "active",
    "accentuation",
    "related_to",
)


class BaseEngine(WithMenu):
    """
    Base engine.
    """

    def __init__(self, track):
        super().__init__()
        self.track = track
        # Settings
        self.pitch = Field(smooth=True)
        self.gravity = Field(default=12, smooth=True)
        self.rythm = Field(smooth=True)
        self.pattern = Field(smooth=True)
        self.basevel = Field(smooth=True)
        self.midi_channel = Field(min_value=0, max_value=15)
        self.active = BooleanField(default=True)
        self.accentuation = Field(default=ACCENT, smooth=True)
        self.related_to = EnumField(choices=["scale", "chord", "static"], default=1)
        self.do_ponctuation = BooleanField(default=False)
        self.lfos = []
        # Internal stuff
        self.pos = Field(max_value=None)
        self.currently_playing_notes = []
        self.chord_number = 1
        self.notes_cache = None
        if "pytest" not in sys.modules:
            pos_y = 300  # Top of the menus
            pos_y += WIDGET_LINE * 2 + WIDGETS_MARGIN  # Size of the session menu
            self.init_menus(pos_y)

    def init_menus(self, pos_y):
        """
        Initialize engine menu.
        """
        self.main_menu = MainEngineGUI(
            self, pos_y=WIDGETS_MARGIN + self.track.track_id * WIDGET_LINE
        )
        self.main_menu.show()
        details = EngineDetailsGUI(self, pos_y=pos_y)
        self.sub_menus.append(details)
        self.sub_menus.append(LFOGUI(self, pos_y=pos_y))

    def next_page(self, go_back=False):
        """
        Show next page
        """
        if not self.sub_menus:
            return False
        active_menu = self.get_active_menu()
        for submenu in self.sub_menus:
            submenu.hide()
        if isinstance(active_menu, bool):
            self.sub_menus[0].show()
            self.sub_menus[0].activate_widget(self.sub_menus[0].default_widget)
            return True
        next_menu = active_menu + (-1 if go_back else 1)
        if next_menu > len(self.sub_menus) - 1 or next_menu < 0:
            self.sub_menus[0].show()
            self.sub_menus[0].activate_widget(self.sub_menus[0].default_widget)
            return False
        self.sub_menus[next_menu].show()
        self.sub_menus[next_menu].activate_widget(
            self.sub_menus[next_menu].default_widget
        )
        return True

    def load(self, data):
        """
        Load from data.
        """
        for loadable_key in LOADABLE_KEYS:
            if loadable_key in data:
                field = getattr(self, loadable_key)
                if isinstance(field, Field):
                    field.set_value(data[loadable_key], force=True)
                else:
                    setattr(self, loadable_key, data[loadable_key])
        for menu in self.sub_menus:
            menu.hide()
        if "visible_menu" in data:
            self.sub_menus[data["visible_menu"]].show()
            if "active_widget" in data:
                self.sub_menus[data["visible_menu"]].activate_widget(
                    data["active_widget"]
                )
        self.engine_load(data)
        self.load_lfos(data.get("lfos", []))

    def engine_load(self, data):
        """
        Method to allow subclasses to have specific load mechanism.
        """

    def save(self, for_reload=False):
        """
        Get data to save this engine.
        """
        result = {
            "type": self.track.engine_type.get_value(),
            "lfos": [lfo.save() for lfo in self.lfos],
        }
        if for_reload:
            result.update(
                {
                    "visible_menu": self.get_visible_menu(),
                    "active_widget": self.sub_menus[
                        self.get_visible_menu()
                    ].active_widget
                    if self.get_visible_menu() is not None
                    else None,
                }
            )
        for savable_key in LOADABLE_KEYS:
            field = getattr(self, savable_key)
            if isinstance(field, Field):
                result[savable_key] = field.value
            else:
                result[savable_key] = field
        result.update(self.engine_save())
        return result

    def engine_save(self):
        """
        Method to allow subclasses to save specific parameters.
        """
        return {}

    @property
    def pattern_str(self):
        """
        Get str representation of the melodic pattern.
        """
        lowest, highest = [
            f"{pygame.midi.midi_to_ansi_note(note):4}" for note in self.get_tessitura()
        ]
        notes = self.notes_cache
        if not notes:
            notes = []
        note_names = ", ".join(
            [f"{pygame.midi.midi_to_ansi_note(note):4}" for note in notes]
        )
        return f"{lowest} < {note_names} < {highest}"

    @property
    def rythm_str(self):
        """
        Get str representation of the rythmic pattern.

        The representation uses 'o' and '.', each character is a thirty-second note
        for example a simple 4/4 rythm will be presented as:

        o.......o.......o.......o.......
        """
        rpat = self.get_rythm_pattern()
        result = []
        for duration in rpat:
            start_symbol = "o"
            sustain_symbol = "."
            if duration < 0:
                start_symbol = " "
                sustain_symbol = " "
                duration = abs(duration)
            duration = int(duration)
            rpr = start_symbol + (
                sustain_symbol * (duration - 1) if duration > 1 else ""
            )
            result.append(rpr)
        return "".join(result)

    @property
    def related_to_str(self):
        """
        Get str representation of the 'related_to' attribute.
        """
        return self.related_to.str_value()

    def midi_tick(self, ticks, timestamp, chord_number):
        """
        Handle Midi tick event.

        Gather positions where the engine should trigger events.
        Gather notes it should play and at which velocity.

        Return event list.
        """
        for lfo in self.lfos:
            lfo.midi_tick(ticks)
        midi_channel = self.midi_channel.get_value()
        self.chord_number = chord_number
        result = []
        rpattern = self.get_rythm_pattern()
        rlength = sum(map(abs, rpattern))
        tick = ticks % rlength
        positions = self.get_positions()
        stop_positions = self.get_stop_positions()
        if self.currently_playing_notes and (
            tick in stop_positions or not self.active.get_value()
        ):
            ponctuation = self.is_ponctuation(tick)
            if ponctuation != PONCTUATION_PART:
                for prevnote in self.currently_playing_notes:
                    result.append((timestamp, "off", midi_channel, prevnote, 0))
                self.currently_playing_notes = []
        if not self.active.get_value():
            return result
        if tick in positions:
            ponctuation = self.is_ponctuation(tick)
            if ponctuation == PONCTUATION_PART:
                return result
            silence = self.is_rest(tick)
            notes = self.get_notes()
            self.notes_cache = notes
            if not silence:
                self.pos.increment()
                vel = self.get_vel(tick)
                for note in notes:
                    if self.active.get_value():
                        result.append((timestamp, "on", midi_channel, note, vel))
                    self.currently_playing_notes.append(note)
        return result

    def get_rythm_pattern(self):
        """
        Get rythmic pattern.
        """
        return RYTHM_PATTERNS[
            int(self.rythm.get_value() * (len(RYTHM_PATTERNS) - 1) / 127)
        ]

    def get_positions(self):
        """
        Get all positions where the engine should trigger Note ON events.
        """
        rpattern = self.get_rythm_pattern()
        positions = [0]
        for duration in rpattern[:-1]:
            positions.append(abs(duration) + positions[-1])
        return positions

    def is_rest(self, tick):
        """
        Decide if given tick should be a note or silence.
        """
        rpattern = self.get_rythm_pattern()
        positions = self.get_positions()
        return rpattern[positions.index(tick)] < 0

    def is_ponctuation(self, tick):
        """
        Decide if the current tick should be considered as a ponctuation.
        """
        if not self.do_ponctuation.get_value():
            return PONCTUATION_NOT
        progression_length = len(self.track.session.chord_progression.get_value())
        progression_pos = self.track.session.progression_pos
        if progression_length < 2:
            # No ponctuation when there is no chord progression (only one chord)
            return PONCTUATION_NOT
        if progression_pos != progression_length - 1:
            # This is not the end of the chord progression
            return PONCTUATION_NOT
        if tick == 0:
            return PONCTUATION_START
        return PONCTUATION_PART

    def get_stop_positions(self):
        """
        Get all positions where the engine should trigger Note OFF events.
        """
        return self.get_positions()

    def get_pattern(self):
        """
        Get melodic pattern.
        """
        return NOTE_PATTERNS[
            int(self.pattern.get_value() * (len(NOTE_PATTERNS) - 1) / 127)
        ]

    def get_tessitura(self, centered=True):
        """
        Get the lowest/highest playable notes.
        """
        delta = int(self.gravity.get_value() / 4)
        pitch = self.pitch.get_value()
        if centered:
            if pitch - delta < 0:
                pitch = delta
            if pitch + delta > 127:
                pitch = 127 - delta
            return (pitch - delta, pitch + delta)
        return (pitch, pitch + delta * 2)

    def get_candidate_notes(self):
        """
        Depending on the engine, get the candidate 'playable' notes.
        """
        if self.related_to.get_value() == "static":
            return [self.pitch.get_value()]
        pattern = self.get_pattern()
        scale_notes = self.track.session.scale.get_value()
        root = self.track.session.root_note.get_value()
        chord_notes = self.track.session.current_chord.get_value()
        notes = []
        for degree in pattern:
            if self.related_to.get_value() == "chord" and chord_notes:
                chord_degree = (
                    chord_notes[(degree - 1) % len(chord_notes)]
                    - 1
                    + self.chord_number
                    - 1
                ) % len(scale_notes)
                note = scale_notes[chord_degree] + root
                if degree > max(chord_notes):
                    note += 12
                notes.append(note)
            elif self.related_to.get_value() == "scale":
                notes.append(scale_notes[(degree - 1) % len(scale_notes)] + root)
        return notes

    def get_notes(self):
        """
        Get playable notes.
        """
        candidates = self.get_candidate_notes()
        transposed = self.transpose_notes(candidates)
        lowest, highest = self.get_tessitura()
        return spread_notes(transposed, lowest, highest)

    def transpose_notes(self, candidates, centered=True):
        """
        Transpose notes based on pitch and gravity.
        """
        lowest, highest = self.get_tessitura(centered)
        notes = []
        for candidate in candidates:
            note = candidate + 12 * (self.pitch.get_value() // 12)
            if note < lowest:
                note += (((lowest - note) // 12) + 1) * 12
            if note > highest:
                note -= (((note - highest) // 12) + 1) * 12
            if note < lowest:
                # note is outside of our tessitura, find the closest equivalent
                if lowest - note > (note + 12 - lowest):
                    note += 12
            notes.append(int(note))
        # Now spread the notes into the whole allowed tessitura
        return notes

    def get_vel(self, tick):
        """
        Get velocity for this tick.

        This is used to generate accentuation based on beat.
        """
        vel = int(self.basevel.get_value() * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation.get_value())
        return max(1, min(vel, 127))

    def stop(self):
        """
        Send Note OFF event for all currently playing notes.
        """
        timestamp = pygame.midi.time()
        midi_channel = self.midi_channel.get_value()
        result = []
        if self.currently_playing_notes:
            for prevnote in self.currently_playing_notes:
                result.append((timestamp, "off", midi_channel, prevnote, 0))
        return result

    def reset_pos(self):
        """
        Reset position.
        """
        self.pos.set_value(0)

    def close(self):
        """
        Stop all notes, unhook menus' widgets and hide.
        """
        super().close()
        return self.stop()

    # LFOs
    def load_lfos(self, data):
        """
        Load LFO setup from data.
        """
        for lfo_data in data:
            self.add_lfo(**lfo_data)

    def add_lfo(self, waveform="squarish", attrname="basevel", depth=0, rate=1, **kw):
        """
        Add an LFO modulating attribute 'attrname'.
        """
        field = getattr(self, attrname)
        setter = getattr(field, "set_modulation")
        lfo = LFO(setter, waveform=waveform, **kw)
        lfo.dest_name.set_value(attrname, force=True)
        lfo.rate.set_value(rate, force=True)
        lfo.depth.set_value(depth, force=True)
        self.lfos.append(lfo)


class BaseArp(BaseEngine):
    """
    Base for all arpegiating engines.
    """

    def get_notes(self):
        notes = super().get_notes()
        return [notes[self.pos.get_value() % len(notes)]]
