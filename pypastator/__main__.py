"""
Pastator.

Pastator is a multi-channel Midi Arpegiator.
"""
import heapq
import json
import os
import traceback

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
    SCR_HEIGHT,
    SCR_WIDTH,
    STOP,
)
from pypastator.engine.session import Session


class Pastator:
    """
    Pastator handles pygame GUI and manages the Midi engines.
    """

    def __init__(self):
        self.out_evts = []
        self.devices = {
            "clock": None,
            "ctrl": [],
            "output": [],
            "note_in": [],
        }
        self.ticks = 0
        self.running = False
        screen_width = SCR_WIDTH
        screen_height = SCR_HEIGHT
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        self.clock = pygame.time.Clock()
        self.session = Session(self)

    def _get_available_midi_devices(self):
        """
        Gather the list of available MIDI devices.
        """
        available_devices = {
            "output": {},
            "input": {},
        }
        for i in range(pygame.midi.get_count()):
            device_info = pygame.midi.get_device_info(i)
            name, is_input, is_output = device_info[1:4]
            if is_input:
                available_devices["input"][name.decode()] = i
            elif is_output:
                available_devices["output"][name.decode()] = i
        return available_devices

    def set_clock_device(self, dev_name=None, dev_id=None):
        """
        Set the MIDI clock device.
        """
        available_devices = self._get_available_midi_devices()
        try:
            if self.devices["clock"] is not None:
                self.devices["clock"].close()
            if dev_id is not None:
                self.devices["clock"] = pygame.midi.Input(dev_id)
                print(f"INFO: clock device [{dev_id}] selected.")
            elif dev_name in available_devices["input"]:
                self.devices["clock"] = pygame.midi.Input(
                    available_devices["input"][dev_name]
                )
                print(f"INFO: clock device [{dev_name}] selected.")
            else:
                print(f"WARN: clock device [{dev_name}] is not available.")
        except:
            print(f"ERROR: Cannot open clock device [{dev_name or dev_id}].")
            traceback.print_exc()
        self.save_settings()

    def add_input_output_device(
        self, dev_name=None, dev_id=None, device_type="ctrl", direction="input"
    ):
        """
        Add an input or output device (input for ctrl or note_in, output for note_out).
        """
        device_class = (
            pygame.midi.Output if direction == "output" else pygame.midi.Input
        )
        available_devices = self._get_available_midi_devices()
        try:
            if dev_id is not None:
                self.devices[device_type].append(device_class(dev_id))
                print(f"INFO: {direction} device [{dev_id}] added for {device_type}.")
            elif dev_name in available_devices[direction]:
                self.devices[device_type].append(
                    device_class(available_devices[direction][dev_name])
                )
                print(f"INFO: {direction} device [{dev_name}] added for {device_type}.")
            else:
                print(f"WARN: {direction} device [{dev_name}] is not available.")
        except:
            print(f"ERROR: Cannot open {direction} device [{dev_name or dev_id}].")
            traceback.print_exc()
        self.save_settings()

    def load_settings(self):
        """
        Load settings from JSON file.
        """
        if not os.path.exists("settings.json"):
            print(f"WARN: no settings.json file found, creating one.")
            self.save_settings()
            return
        with open("settings.json", "r", encoding="utf8") as file_pointer:
            data = json.load(file_pointer)
            for key, value in data.get("devices", {}).items():
                if key not in self.devices:
                    continue
                if key == "clock":
                    self.set_clock_device(value)
                elif key in ("ctrl", "note_in"):
                    for dev_name in value:
                        self.add_input_output_device(dev_name=dev_name, device_type=key)
                elif key == "output":
                    for dev_name in value:
                        self.add_input_output_device(
                            dev_name=dev_name, device_type=key, direction="output"
                        )

    def save_settings(self):
        """
        Save settings to JSON file.
        """
        data = {
            "devices": {
                "clock": None,
                "ctrl": [],
                "note_in": [],
                "output": [],
            }
        }
        for device_type, devices in self.devices.items():
            if device_type == "clock":
                device = devices
                if device is not None:
                    data["devices"][device_type] = pygame.midi.get_device_info(
                        device.device_id
                    )[1].decode()
                continue
            for device in devices:
                data["devices"][device_type].append(
                    pygame.midi.get_device_info(device.device_id)[1].decode()
                )
        with open("settings.json", "w", encoding="utf8") as file_pointer:
            json.dump(data, file_pointer, indent=2)

    def load(self, filename):
        """
        Load a song.
        """
        self.session.load(filename)

    def handle_clock_in_event(self, evt):
        """
        Handle Midi clock event.
        """
        typ = evt[0][0]
        if typ == CLOCK:
            self.midi_tick()
        elif typ == PLAY:
            self.session.playing = self.ticks
        elif typ == STOP:
            self.session.stop()
            self.all_sound_off()

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
            cc_channel = typ - 176
            cc_number = data1
            cc_value = data2
            self.session.handle_cc(cc_channel, cc_number, cc_value)

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
        elif ui_evt.type == pygame.MOUSEBUTTONUP:
            self.session.handle_click(ui_evt.pos, ui_evt.button)
        elif ui_evt.type == pygame.MOUSEMOTION:
            self.session.handle_mouse_move(ui_evt.pos)

    def run(self):
        """
        Main loop.
        """
        self.running = True
        while self.running:
            pygame.event.pump()
            self.clock.tick()
            self.session.handle_tick()
            ui_evts = pygame.event.get()
            for ui_evt in ui_evts:
                self.handle_ui_event(ui_evt)
            if self.devices["clock"] is not None:
                if self.devices["clock"].poll():
                    for evt in self.devices["clock"].read(10):
                        self.handle_clock_in_event(evt)
            for ctrl_device in self.devices["ctrl"]:
                if ctrl_device.poll():
                    for evt in ctrl_device.read(10):
                        self.handle_ctrl_in_event(evt)
            self.handle_out_events()
            pygame.display.flip()
        self.all_sound_off()

    def all_sound_off(self):
        """
        Turn off all the notes on all Midi channels.
        """
        for output_device in self.devices["output"]:
            for channel in range(16):
                output_device.write_short(CCMIN + channel, ALL_NOTES_OFF)
                output_device.write_short(CCMIN + channel, ALL_SOUND_OFF)

    def midi_tick(self):
        """
        Pass Midi tick events to session and get the outgoing events.
        """
        self.ticks += 1
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
        for output_device in self.devices["output"]:
            if evt_type == "on":
                note, velocity = evt[3:5]
                output_device.note_on(note, velocity, evt_channel)
            elif evt_type == "off":
                note = evt[3]
                output_device.note_off(note, 0, evt_channel)


def main():
    """
    Main entry point for the software.
    """
    pygame.midi.init()
    pygame.display.init()
    pygame.font.init()

    pasta = Pastator()
    pasta.load_settings()
    pasta.all_sound_off()
    pasta.load("default.json")
    pasta.run()


if __name__ == "__main__":
    main()
