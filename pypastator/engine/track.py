"""
Track holds the details about the musical engine of a particular track.
"""
from pypastator.constants import (
    ENGINE_TYPE_ARP,
    ENGINE_TYPE_CHORD,
    ENGINE_TYPE_STRUM,
    ENGINE_TYPES,
)
from pypastator.engine.arp import Arp
from pypastator.engine.chord import Chord
from pypastator.engine.field import EnumField
from pypastator.engine.lfo import get_lfo
from pypastator.engine.strum import Strum
from pypastator.widgets.gui.base import WithMenu


class Track(WithMenu):
    """
    Definition of a track.
    """

    def __init__(self, track_id, session):
        super().__init__()
        self.track_id = track_id
        self.session = session
        self.engine = None
        self.engine_type = EnumField(choices=ENGINE_TYPES)
        self.engine_type.hook(self.set_type, "track_set_type")
        self.lfos = []

    @property
    def engine_type_str(self):
        """
        Get the str representation of the engine type.
        """
        return self.engine_type.str_value()

    def set_type(self, engine_type=ENGINE_TYPE_ARP):
        """
        Set the type of engine used by the track.
        """
        change = self.engine is not None
        data = {}
        if change:
            data = self.engine.save()
            for evt in self.engine.close():
                self.session.pasta.emit_out_event(evt)
        if engine_type == ENGINE_TYPE_ARP:
            self.engine = Arp(self)
        elif engine_type == ENGINE_TYPE_CHORD:
            self.engine = Chord(self)
        elif engine_type == ENGINE_TYPE_STRUM:
            self.engine = Strum(self)
        if change:
            self.engine.load(data)

    def load_lfos(self, data):
        """
        Load LFO setup from data.
        """
        for lfo_data in data:
            self.add_lfo(**lfo_data)

    def load(self, data):
        """
        Load a track from data.
        """
        engine_type = ENGINE_TYPES.index(data.get("type", "arp"))
        self.engine_type.set_value(engine_type)
        self.engine.load(data)
        self.load_lfos(data.get("lfos", []))

    def midi_tick(self, ticks, timestamp, chord):
        """
        Handle Midi tick event.
        """
        for lfo in self.lfos:
            lfo.midi_tick(ticks)
        if self.engine is not None:
            return self.engine.midi_tick(ticks, timestamp, chord)
        return []

    def handle_click(self, pos):
        """
        Pass click event to this track's widgets.
        """
        super().handle_click(pos)
        if self.engine is not None:
            self.engine.handle_click(pos)

    def add_lfo(self, waveform="squarish", attrname="vel", depth=0, rate=1, **kw):
        """
        Add an LFO modulating attribute 'attrname'.
        """
        field = getattr(self.engine, attrname)
        setter = getattr(field, "set_modulation")
        lfo = get_lfo(setter, waveform=waveform, **kw)
        lfo.rate.set_value(rate, force=True)
        lfo.depth.set_value(depth, force=True)
        self.lfos.append(lfo)

    def handle_cc(self, cc_channel, cc_number, cc_value):
        """
        Handle Midi CC events.
        """
        super().handle_cc(cc_channel, cc_number, cc_value)
        if self.engine is not None:
            self.engine.handle_cc(cc_channel, cc_number, cc_value)
