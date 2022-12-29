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
# Channel used for menu control via Midi CC
MENU_CC_CHANNEL = 15
# Midi CC numbers for menu control
MENU_CC_PREV_PAGE = 1
MENU_CC_NEXT_PAGE = 0
MENU_CC_INCR = 2
MENU_CC_DECR = 3
MENU_CC_NEXT_WIDGET = 4
ENGINE_CC_BASEVEL = 0
ENGINE_CC_PATTERN = 1
ENGINE_CC_RYTHM = 2
ENGINE_CC_PITCH = 3
ENGINE_CC_MUTE = 4
ENGINE_CC_SELECT = 5

# UI constants
KNOB_ANGLE = math.pi
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
FONT_NAME = "JuliaMono-Bold.ttf"
EMOJI_FONT_NAME = "NotoEmoji-Bold.ttf"
FONT_SIZE = 20
EMOJI_FONT_SIZE = 14
BASE_WIDGET_HEIGHT = 24
BASE_WIDGET_WIDTH = 80
SMALL_FONT_NAME = "JuliaMono-Bold.ttf"
SMALL_FONT_SIZE = 20
MESSAGE_FONT_SIZE = 14
WIDGETS_MARGIN = 10
BUTTON_WIDTH = 80
SLIDER_WIDTH = 400
KNOB_SIZE = BASE_WIDGET_HEIGHT
WIDGET_LABEL_SIZE = 80
LED_SIZE = BASE_WIDGET_HEIGHT
WIDGET_LINE = BASE_WIDGET_HEIGHT + WIDGETS_MARGIN
LEFT_COL = WIDGETS_MARGIN * 2 + BUTTON_WIDTH
BIG_LABEL_W = SLIDER_WIDTH + BUTTON_WIDTH + WIDGETS_MARGIN
MOUSE_WHEEL_UP = 4
MOUSE_WHEEL_DOWN = 5

# Melodic constants
# Durations
THIRTYSECOND = 3
SIXTEENTH = 2 * THIRTYSECOND
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
DEFAULT_STRUMMING = 3

# Patterns
# Those number represent positions in the chord
#  (or in the scale if related_to is set to "scale")
# For example, in a triad:
# - 1 is the root
# - 2 is the third
# - 3 is the fifth
NOTE_PATTERNS = [
    (3, 1, 1),
    (3, 1, 2),
    (3, 2, 1),
    (3, 2, 1, 2),
    (3, 2, 2),
    (3, 2, 3, 4),
    (3, 3, 2),
    (3, 3, 3, 4),
    (1, 1, 1),
    (1, 1, 2),
    (1, 2, 2),
    (1, 2, 3),
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
    (DEIGHTH, DEIGHTH, EIGHTH, HALF),
    (QUARTER, QUARTER, EIGHTH, EIGHTH, QUARTER),
    (QUARTER, DQUARTER, EIGHTH, EIGHTH, EIGHTH),
    (EIGHTH, QUARTER, EIGHTH, QUARTER, SIXTEENTH, SIXTEENTH, EIGHTH),
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
# Here the numbers represent semitones from the root
# - 3 is a minor third
# - 4 is a major third
# - ...
SCALES = [
    [0, 2, 4, 5, 7, 9, 11],
    [0, 2, 3, 5, 7, 8, 10],
]
# Here the numbers represent positions in the scale:
# - 1 is the root
# - 3 is the third
# - 5 is the fifth
# - ...
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
ENGINE_TYPE_ARP, ENGINE_TYPE_CHORD, ENGINE_TYPE_STRUM, ENGINE_TYPE_MELOTOR = (0, 1, 2, 3)
ENGINE_TYPES = ["arp", "chord", "strum", "melotor"]

# Drum notes for MC-101
KICK = 36
RIM = 37
SNARE = 38
CLAP = 39
LTOM = 41
CHH = 42
MTOM = 45
OHH = 46
HTOM = 48
RIDE = 49
CRASH = 51
TAMB = 54
COW = 56
PERC1 = 62  # Conga high
PERC2 = 63  # Conga med
PERC3 = 64  # Conga low
