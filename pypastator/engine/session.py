from engine.track import Track
from constants import BAR

class Session:
    def __init__(self):
        self.scale_name = "major"
        self.chord_progression = [1, 3, 4, 6]
        self.current_chord = 0
        self.tracks = {
            0: Track(0)
        }
        self.playing = False
        self.cc_controls = {}

    def midi_tick(self, ticks, timestamp):
        if not self.playing:
            return []
        relative_ticks = ticks - self.playing
        if relative_ticks % BAR == 0:
            self.current_chord = int(relative_ticks / BAR) % len(self.chord_progression)
            print("bar", self.current_chord, self.playing, relative_ticks)
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
                self.tracks[track_id] = Track(track_id)
            print("track", cc - 48)
