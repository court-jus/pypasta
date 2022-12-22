"""
Constants used in Pastator.
"""
import math

# Midi events types
CLOCK = 248
NOTEON = 144
NOTEOFF = 128
# CC is 0xB0 (176) + channel (0 indexed)
CCMIN = 176
CCMAX = 191
ALL_NOTES_OFF = 123
ALL_SOUND_OFF = 120
PLAY = 250
STOP = 252

# UI constants
KNOB_ANGLE = math.pi
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
FONT_NAME = "JuliaMono-Bold.ttf"
EMOJI_FONT_NAME = "NotoEmoji-Bold.ttf"
FONT_SIZE = 20
EMOJI_FONT_SIZE = 18
BASE_WIDGET_HEIGHT = 24
BASE_WIDGET_WIDTH = 80
SMALL_FONT_NAME = "JuliaMono-Bold.ttf"
SMALL_FONT_SIZE = 20
WIDGETS_MARGIN = 10
BUTTON_WIDTH = 80
SLIDER_WIDTH = 400
KNOB_SIZE = BASE_WIDGET_HEIGHT
WIDGET_LABEL_SIZE = 80
LED_SIZE = BASE_WIDGET_HEIGHT

# Melodic constants
# Durations
SIXTEENTH = 6
DSIXTEENTH = SIXTEENTH * 1.5
EIGHTH = 12
DEIGHTH = EIGHTH * 1.5
QUARTER = 24
DQUARTER = QUARTER * 1.5
HALF = 48
DHALF = HALF * 1.5
FULL = 96
BEAT = QUARTER
BAR = FULL

# Patterns
NOTE_PATTERNS = [
    (3, 1, 1),
    (3, 1, 2),
    (3, 2, 1),
    (3, 2, 2),
    (3, 2, 3, 4),
    (3, 3, 2),
    (3, 3, 3, 4),
    (1, 1, 1),
    (1, 1, 2),
    (1, 2, 2),
    (1, 2, 3, 3),
    (1, 2, 3, 4),
    (1, 3, 2),
    (1, 3, 3),
    (1, 3, 3, 4),
    (1, 2, 3, 4, 5),
    (8, 8, 7, 8, 5, 5, 4, 5),
]

RYTHM_PATTERNS = [
    (FULL,),
    (HALF, HALF),
    (QUARTER, DHALF),
    (QUARTER, QUARTER, HALF),
    (HALF, EIGHTH, DQUARTER),
    (QUARTER, QUARTER, QUARTER, QUARTER),
    (QUARTER, QUARTER, EIGHTH, EIGHTH, QUARTER),
    (QUARTER, DQUARTER, EIGHTH, EIGHTH, EIGHTH),
    (EIGHTH, DEIGHTH, EIGHTH, QUARTER, SIXTEENTH, SIXTEENTH, EIGHTH),
    (EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH),
    (
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
    ),
]

# Other
ACCENT = 1.5
SCALE_NAMES = ["major", "minor"]
SCALES = [
    [0, 2, 4, 5, 7, 9, 11],
    [0, 3, 4, 5, 7, 8, 10],
]
CHORDS = [
    [1, 3, 5],
    [1, 3, 5, 7],
    [3, 5, 7],
    [1, 3, 5, 9],
    [1, 3, 7, 9],
    [1, 3, 5, 7, 9, 11],
    [1, 2, 5],
    [1, 4, 5],
    [1, 3, 6],
    [1, 3, 6, 7],
]
ENGINE_TYPE_ARP, ENGINE_TYPE_CHORD, ENGINE_TYPE_STRUM = (0, 1, 2)
ENGINE_TYPES = ["arp", "chord", "strum"]
