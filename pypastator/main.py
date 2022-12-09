import random
import pygame.font
import pygame.midi
import time
import heapq


CLOCK = 248
NOTEON = 144
NOTEOFF = 128
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FONT_SIZE = 24
WIDGETS_MARGIN = 10
BUTTON_WIDTH = 200
SLIDER_WIDTH = 400
SLIDER_BUTTON_SIZE = 150


class Label:
    def __init__(self, msg, fcolor=WHITE, bcolor=RED, w=BUTTON_WIDTH, h=FONT_SIZE*2, x=WIDGETS_MARGIN, y=WIDGETS_MARGIN):
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.width, self.height = w, h

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x + int(self.width / 2), y)

        self.msg_image = self.font.render(msg, True, self.fcolor, self.bcolor)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw(self):
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        pygame.display.get_surface().fill(self.fcolor, self.rect)
        pygame.display.get_surface().fill(self.bcolor, brect)
        pygame.display.get_surface().blit(self.msg_image, self.msg_image_rect)


class Slider:
    def __init__(self, msg, fcolor=WHITE, bcolor=RED, w=SLIDER_WIDTH, h=FONT_SIZE + 2, x=WIDGETS_MARGIN, y=WIDGETS_MARGIN):
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.x, self.y = x + SLIDER_BUTTON_SIZE + WIDGETS_MARGIN, y
        self.width, self.height = w, h
        self.value = 64
        self.font = pygame.font.SysFont(None, FONT_SIZE)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x + int(self.width / 2), y + int(self.height / 2))
        
        self.label = Label(msg, fcolor, bcolor, SLIDER_BUTTON_SIZE, h, x, self.rect.center[1])

    def draw(self):
        self.label.draw()
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        txt = self.font.render(str(self.value), True, self.fcolor, self.bcolor)
        cursor = pygame.Rect(0, 0, 5, self.height)
        cursor.center = (self.x + int(self.value*self.width / 127), self.rect.center[1])
        pygame.display.get_surface().fill(self.fcolor, self.rect)
        pygame.display.get_surface().fill(self.bcolor, brect)
        pygame.display.get_surface().blit(txt, (self.rect.center[0], self.rect.center[1] - (FONT_SIZE / 4)))
        pygame.display.get_surface().fill(self.fcolor, cursor)


class Pastator:
    def __init__(self, channel_in, channel_out):
        self.out_evts = []
        self.channel_in = channel_in
        self.channel_out = channel_out
        self.clock = 0
        screen_width = 1024
        screen_height = 768
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        self.clock = pygame.time.Clock()
        self.slider = Slider("hey")
        self.slider.draw()

    def handle_in_event(self, evt):
        [[typ, data1, data2, data3], timestamp] = evt
        if typ == CLOCK:
            self.clock += 1
            self.run_engine()
        elif typ in (NOTEON, NOTEOFF):
            note = data1
            note_name = pygame.midi.midi_to_ansi_note(note)
            velocity = data2
            if typ == NOTEON:
                print(timestamp, "play", note_name, "vel", velocity)
            else:
                # print("stop", note_name,"vel",velocity)
                pass
        else:
            print(evt)

    def run(self, how_long=10000):
        maxt = pygame.time.get_ticks() + how_long
        start = pygame.time.get_ticks()
        prev = pygame.time.get_ticks()
        while pygame.time.get_ticks() < maxt:
            pygame.event.pump()
            self.clock.tick()
            now = pygame.time.get_ticks()
            if self.channel_in is not None:
                if self.channel_in.poll():
                    for evt in self.channel_in.read(10):
                        self.handle_in_event(evt)
            self.handle_out_events()
            pygame.display.flip()
            if int((now - start) * 25) !=  int((prev - start) * 25):
                self.slider.value = random.randint(0, 127)
                self.slider.draw()
                print(maxt - now)
            prev = now

    def run_engine(self):
        timestamp = pygame.midi.time()
        if self.clock % 24 == 0:
            chosen_note = random.choice([60, 63, 67])
            heapq.heappush(self.out_evts, (timestamp, "on", chosen_note, 96))
            heapq.heappush(self.out_evts, (timestamp + 20, "off", chosen_note, 0))

    def handle_out_events(self):
        timestamp = pygame.midi.time()
        while self.out_evts and self.out_evts[0][0] < timestamp:
            evt = heapq.heappop(self.out_evts)
            evt_type = evt[1]
            if evt_type == "on" and self.channel_out is not None:
                self.channel_out.note_on(evt[2], evt[3])
            elif evt_type == "off" and self.channel_out is not None:
                self.channel_out.note_off(evt[2], evt[3])


def main():

    pygame.midi.init()
    pygame.display.init()
    pygame.font.init()

    print("=================")

    from_reaper_name = "Virtual RawMIDI"
    to_reaper_name = "Virtual RawMIDI"
    from_reaper = None
    to_reaper = None

    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        interf, name, is_input, is_output, is_opened = r
        if name.decode() == from_reaper_name and is_input:
            print("From", interf, name, is_input, is_output, is_opened)
            from_reaper = pygame.midi.Input(i)
        if name.decode() == to_reaper_name and is_output:
            print("To", interf, name, is_input, is_output, is_opened)
            to_reaper = pygame.midi.Output(i)

    print(f"reaper -{from_reaper}-> us -{to_reaper}-> reaper")

    if to_reaper:
        to_reaper.note_on(60, 96)
        pygame.time.wait(100)
        to_reaper.note_off(60, 96)
        pygame.time.wait(100)
        to_reaper.note_on(63, 96)
        pygame.time.wait(100)
        to_reaper.note_off(63, 96)
        pygame.time.wait(100)
        to_reaper.note_on(67, 96)
        pygame.time.wait(100)
        to_reaper.note_off(67, 96)
        pygame.time.wait(100)

    pasta = Pastator(from_reaper, to_reaper)
    pasta.run()

    print("================")


if __name__ == "__main__":
    main()
