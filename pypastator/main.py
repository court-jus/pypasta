import heapq
import random

import pygame.font
import pygame.midi
from constants import (ALL_NOTES_OFF, ALL_SOUND_OFF, CCMAX, CCMIN, CLOCK,
                       KNOB_LABEL_SIZE, KNOB_SIZE, NOTEOFF, NOTEON, SIXTEENTH,
                       SLIDER_LABEL_SIZE, SLIDER_WIDTH, WIDGETS_MARGIN, PLAY, STOP)
from engine.session import Session


class Pastator:
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
        self.session = Session()

    def handle_in_event(self, evt):
        [[typ, data1, data2, data3], timestamp] = evt
        if typ == CLOCK:
            self.midi_tick()
            self.ticks += 1
        elif typ == PLAY:
            self.session.playing = self.ticks
        elif typ == STOP:
            self.session.playing = False
            self.all_sound_off()
        elif typ in (NOTEON, NOTEOFF):
            note = data1
            note_name = pygame.midi.midi_to_ansi_note(note)
            velocity = data2
            if typ == NOTEON:
                print(timestamp, "receive note_on", note_name, "vel", velocity)
            else:
                print(timestamp, "receive note_off", note_name,"vel",velocity)
        elif typ >= CCMIN and typ <= CCMAX:
            cchannel = typ - 176
            cc = data1
            value = data2
            self.session.handle_cc(cchannel, cc, value)
        else:
            print(evt)

    def run(self):
        self.running = True
        while self.running:
            pygame.event.pump()
            self.clock.tick()
            ui_evts = pygame.event.get()
            for ui_evt in ui_evts:
                if ui_evt.type == pygame.QUIT:
                    self.running = False
                elif ui_evt.type == pygame.KEYDOWN:
                    if ui_evt.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        print("Key", ui_evt)
                elif ui_evt.type != pygame.MOUSEMOTION:
                    print(ui_evt)
            if self.clock_device is not None:
                if self.clock_device.poll():
                    for evt in self.clock_device.read(10):
                        self.handle_in_event(evt)
            if self.ctrl_device is not None:
                if self.ctrl_device.poll():
                    for evt in self.ctrl_device.read(10):
                        self.handle_in_event(evt)
            self.handle_out_events()
            pygame.display.flip()
        self.all_sound_off()

    def all_sound_off(self):
        if self.output_device is not None:
            for channel in range(16):
                self.output_device.write_short(CCMIN + channel, ALL_NOTES_OFF)
                self.output_device.write_short(CCMIN + channel, ALL_SOUND_OFF)
    
    def midi_tick(self):
        timestamp = pygame.midi.time()
        for evt in self.session.midi_tick(self.ticks, timestamp):
            heapq.heappush(self.out_evts, evt)

    def handle_out_events(self):
        timestamp = pygame.midi.time()
        while self.out_evts and self.out_evts[0][0] <= timestamp:
            evt = heapq.heappop(self.out_evts)
            evt_type = evt[1]
            evt_channel = evt[2]
            if evt_type == "on" and self.output_device is not None:
                note, velocity = evt[3:5]
                print(timestamp, "play", pygame.midi.midi_to_ansi_note(note), velocity)
                self.output_device.note_on(note, velocity, evt_channel)
            elif evt_type == "off" and self.output_device is not None:
                note = evt[3]
                self.output_device.note_off(note, 0, evt_channel)


def main():

    pygame.midi.init()
    pygame.display.init()
    pygame.font.init()

    print("=================")

    clock_device_name = "MC-101"
    output_device_name = "MC-101"
    ctrl_device_name = "Launch Control XL"
    clock_device = None
    ctrl_device = None
    output_device = None
    print("MIDI Devices detected:")
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        interf, name, is_input, is_output, is_opened = r
        if is_input:
            if name.decode() == clock_device_name:
                clock_device = pygame.midi.Input(i)
            elif name.decode() == ctrl_device_name:
                ctrl_device = pygame.midi.Input(i)
            else:
                print(f" - Input [{name.decode()}] available but unused")
        if is_output:
            if name.decode() == output_device_name and is_output:
                output_device = pygame.midi.Output(i)
            else:
                print(f" - Output [{name.decode()}] available but unused")

    print("Devices used:")
    print(
        f" - Clock - {pygame.midi.get_device_info(clock_device.device_id)[1].decode()}"
    )
    print(
        f" - Controller - {pygame.midi.get_device_info(ctrl_device.device_id)[1].decode()}"
    )
    print(
        f" - Sound output - {pygame.midi.get_device_info(output_device.device_id)[1].decode()}"
    )

    pasta = Pastator(clock_device, ctrl_device, output_device)
    pasta.all_sound_off()
    pasta.run()

    print("================")


if __name__ == "__main__":
    main()
