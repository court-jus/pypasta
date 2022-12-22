```
C:/Users/gl/AppData/Local/Programs/Python/Python310/python.exe -m pip install --user pipx
C:\Users\gl\AppData\Roaming\Python\Python310\Scripts\pipx.exe install poetry
C:\Users\gl\.local\bin\poetr
```

# Notes for later

Set colors of the Novation LaunchControlXL buttons.

```
    note = 61
    #print(note)
    channel = 15
    velocity = 15
    print(channel, note)
    ctrl_out_device.note_on(note, velocity=velocity, channel=channel)
    time.sleep(0.01)
    ctrl_out_device.note_off(note, velocity=velocity, channel=channel)

    ctrl_out_device.write([[[176, 0, 0], 0]])
    for led in range(48):
        print(led)
        ctrl_out_device.write_sys_ex(pygame.midi.time(), [240, 0, 32, 41, 2, 17, 120, 0, led, 15, 247])
        time.sleep(0.2)
    ctrl_out_device.write_sys_ex(pygame.midi.time(), [240, 0, 32, 41, 2, 17, 120, 0, 41, 11, 247])
    for vel in range(128):
        ctrl_out_device.write_sys_ex(pygame.midi.time(), [240, 0, 32, 41, 2, 17, 120, 0, 43, vel, 247])
        time.sleep(0.05)
    time.sleep(0.1)
    ctrl_out_device.write([[[176, 0, 0], 0]])
```