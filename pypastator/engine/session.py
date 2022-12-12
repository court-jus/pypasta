from engine.track import Track
from constants import BAR

DEFAULT_TRACK = {
    "type": "arp",
    "pitch": 40,
    "rythm": 100,
    "pattern": 100,
    "basevel": 100,
    "midi_channel": 10,
    "mute": True
}


class Session:
    def __init__(self):
        self.scale_name = "major"
        self.chord_progression = [1]
        self.current_chord = 0
        self.tracks = {}
        self.playing = True
        self.cc_controls = {}

    def load(self, data):
        for loadable_key in ("scale_name", "chord_progression", "playing"):
            if loadable_key in data:
                setattr(self, loadable_key, data[loadable_key])
        for track_id, track in data.get("tracks", {}).items():
            track_id = int(track_id)
            t = Track(track_id)
            t.load(track)
            self.tracks[track_id] = t

    def midi_tick(self, ticks, timestamp):
        if not self.playing:
            return []
        relative_ticks = ticks - self.playing
        if relative_ticks % BAR == 0:
            self.current_chord = int(relative_ticks / BAR) % len(self.chord_progression)
        out_evts = []
        for track in self.tracks.values():
            out_evts.extend(track.midi_tick(relative_ticks, timestamp, self.chord_progression[self.current_chord]))
        return out_evts

    def handle_cc(self, cchannel, cc, value):
        if cchannel != 15:
            print(f"Ignored CC on channel {cchannel}, {cc}, {value}")
            return False

        for track_id, track in self.tracks.items():
            track.handle_cc(cc, value)

        if cc >= 48 and cc <= 56 and value == 127:
            track_id = cc - 48
            if track_id in self.tracks:
                self.tracks[track_id].menu()
            else:
                t = Track(track_id)
                t.load(DEFAULT_TRACK)
                self.tracks[track_id] = t
            print("track", cc - 48)
