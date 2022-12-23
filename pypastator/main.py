"""
Pastator.

Pastator is a multi-channel Midi Arpegiator.
"""
import heapq
import json

import pygame.font
import pygame.midi

from pypastator.constants import (
    ALL_NOTES_OFF,
    ALL_SOUND_OFF,
    CCMAX,
    CCMIN,
    CLOCK,
    NOTEOFF,
    NOTEON,
    PLAY,
    STOP,
)
from pypastator.engine.session import Session


class Pastator:
    """
    Pastator handles pygame GUI and manages the Midi engines.
    """

    def __init__(self, clock_device, ctrl_device, output_device):
        self.out_evts = []
        self.clock_device = clock_device
        self.ctrl_device = ctrl_device
        self.output_device = output_device
        self.ticks = 0
        self.running = False
        screen_width = 1024
        screen_height = 768
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        self.clock = pygame.time.Clock()
        self.session = Session(self)

    def load(self, filename):
        """
        Load a song.
        """
        with open(filename, "r", encoding="utf8") as file_pointer:
            data = json.load(file_pointer)
            self.session.load(data)

    def handle_clock_in_event(self, evt):
        """
        Handle Midi clock event.
        """
        typ = evt[0][0]
        if typ == CLOCK:
            self.midi_tick()
            self.ticks += 1
        elif typ == PLAY:
            self.session.playing = self.ticks
        elif typ == STOP:
            self.session.stop()
            self.all_sound_off()
        else:
            print("Unkown clock event", evt)

    def handle_ctrl_in_event(self, evt):
        """
        Handle Midi CC event.
        """
        [[typ, data1, data2, _], timestamp] = evt
        if typ in (NOTEON, NOTEOFF):
            note = data1
            note_name = pygame.midi.midi_to_ansi_note(note)
            velocity = data2
            if typ == NOTEON:
                print("Received Note ON evt", timestamp, note_name, "vel", velocity)
            else:
                print("Received Note OFF evt", note_name, "vel", velocity)
        elif CCMIN <= typ <= CCMAX:
            cchannel = typ - 176
            cc_number = data1
            value = data2
            self.session.handle_cc(cchannel, cc_number, value)
        else:
            print("Unkown ctrl event", evt)

    def handle_ui_event(self, ui_evt):
        """
        Handle UI events (keyboard/mouse).
        """
        if ui_evt.type == pygame.QUIT:
            self.running = False
        elif ui_evt.type == pygame.KEYDOWN:
            if ui_evt.key == pygame.K_ESCAPE:
                self.running = False
            else:
                print("Key", ui_evt)
        elif ui_evt.type == pygame.MOUSEBUTTONDOWN:
            self.session.handle_click(ui_evt.pos)

    def run(self):
        """
        Main loop.
        """
        self.running = True
        while self.running:
            pygame.event.pump()
            self.clock.tick()
            ui_evts = pygame.event.get()
            for ui_evt in ui_evts:
                self.handle_ui_event(ui_evt)
            if self.clock_device is not None:
                if self.clock_device.poll():
                    for evt in self.clock_device.read(10):
                        self.handle_clock_in_event(evt)
            if self.ctrl_device is not None:
                if self.ctrl_device.poll():
                    for evt in self.ctrl_device.read(10):
                        self.handle_ctrl_in_event(evt)
            self.handle_out_events()
            pygame.display.flip()
        self.all_sound_off()

    def all_sound_off(self):
        """
        Turn off all the notes on all Midi channels.
        """
        if self.output_device is not None:
            for channel in range(16):
                self.output_device.write_short(CCMIN + channel, ALL_NOTES_OFF)
                self.output_device.write_short(CCMIN + channel, ALL_SOUND_OFF)

    def midi_tick(self):
        """
        Pass Midi tick events to session and get the outgoing events.
        """
        timestamp = pygame.midi.time()
        for evt in self.session.midi_tick(self.ticks, timestamp):
            heapq.heappush(self.out_evts, evt)

    def handle_out_events(self):
        """
        Handle outgoing events.
        """
        timestamp = pygame.midi.time()
        while self.out_evts and self.out_evts[0][0] <= timestamp:
            evt = heapq.heappop(self.out_evts)
            self.emit_out_event(evt)

    def emit_out_event(self, evt):
        """
        Emit an outgoing event to a Midi channel.
        """
        evt_type = evt[1]
        evt_channel = evt[2]
        if evt_type == "on" and self.output_device is not None:
            note, velocity = evt[3:5]
            self.output_device.note_on(note, velocity, evt_channel)
        elif evt_type == "off" and self.output_device is not None:
            note = evt[3]
            self.output_device.note_off(note, 0, evt_channel)


def main():
    """
    Main entry point for the software.
    """
    pygame.midi.init()
    pygame.display.init()
    pygame.font.init()

    print("=================")

    clock_device_name = "MC-101"
    output_device_name = "MC-101"
    ctrl_device_name = "Launch Control XL"
    ctrl_out_device_name = "Launch Control XL"
    # clock_device_name = "OP-Z MIDI 1"
    # output_device_name = "OP-Z MIDI 1"
    # ctrl_device_name = "OP-Z MIDI 1"
    clock_device = None
    ctrl_device = None
    ctrl_out_device = None
    output_device = None
    print("MIDI Devices detected:")
    for i in range(pygame.midi.get_count()):
        device_info = pygame.midi.get_device_info(i)
        name, is_input, is_output = device_info[1:4]
        if is_input:
            if name.decode() == clock_device_name:
                clock_device = pygame.midi.Input(i)
            elif name.decode() == ctrl_device_name:
                ctrl_device = pygame.midi.Input(i)
            else:
                print(f" - Input [{name.decode()}] available but unused")
        if is_output:
            if name.decode() == output_device_name:
                output_device = pygame.midi.Output(i)
            if name.decode() == ctrl_out_device_name:
                ctrl_out_device = pygame.midi.Output(i)
            else:
                print(f" - Output [{name.decode()}] available but unused")

    print("Devices used:")
    if clock_device:
        print(
            f" - Clock - {pygame.midi.get_device_info(clock_device.device_id)[1].decode()}"
        )
    if ctrl_device:
        print(
            f" - Controller - {pygame.midi.get_device_info(ctrl_device.device_id)[1].decode()}"
        )
    if ctrl_out_device:
        print(
            " - Controller (out) - "
            f"{pygame.midi.get_device_info(ctrl_out_device.device_id)[1].decode()}"
        )
    if output_device:
        print(
            f" - Sound output - {pygame.midi.get_device_info(output_device.device_id)[1].decode()}"
        )
    pasta = Pastator(clock_device, ctrl_device, output_device)
    pasta.all_sound_off()
    pasta.load("example.json")
    pasta.run()
    print("================")


if __name__ == "__main__":
    main()
