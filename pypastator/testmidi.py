import pygame.midi

pygame.midi.init()

class MidiTester:
    def __init__(self):
        """
        Open all 'input' devices
        """
        self.input_devices = {}
        self.tick = 0
        for i in range(pygame.midi.get_count()):
            device_info = pygame.midi.get_device_info(i)
            name, is_input, is_output = device_info[1:4]
            if is_input:
                self.input_devices[name.decode()] = pygame.midi.Input(i)
                print(f" - Input [{name.decode()}] available")
            if is_output:
                print(f" - Output [{name.decode()}] available")

    def run(self):
        """
        Now loop and look at their events
        """
        self.running = True
        while self.running:
            for name, device in self.input_devices.items():
                if device.poll():
                    for evt in device.read(10):
                        self.handle_in_event(evt, name)

    def handle_in_event(self, evt, devname):
        evt_data = evt[0]
        if evt_data[0] == 248:
            # clock
            self.tick += 1
            if self.tick % 10 == 0:
                print(devname, evt, self.tick)
        else:
            print(devname, evt)

def main():
    tester = MidiTester()
    tester.run()

if __name__ == "__main__":
    main()
