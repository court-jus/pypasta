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
CC_RIGHT_ARROW = 0
CC_LEFT_ARROW = 1
CC_UP_ARROW = 2
CC_DOWN_ARROW = 3
MENU_CC_NEXT_WIDGET = 4
ENGINE_CC_BASEVEL = 0
ENGINE_CC_PATTERN = 1
ENGINE_CC_RYTHM = 2
ENGINE_CC_PITCH = 3
ENGINE_CC_MUTE = 4
ENGINE_CC_SELECT = 5

# UI constants
SCR_WIDTH = 1024
SCR_HEIGHT = 768
FULLSCREEN = True
KNOB_ANGLE = math.pi
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
DARKEST_GRAY = (25, 25, 25)
FONT_NAME = "JuliaMono-Bold.ttf"
EMOJI_FONT_NAME = "NotoEmoji-Bold.ttf"
FONT_SIZE = 20
EMOJI_FONT_SIZE = 14
BASE_WIDGET_HEIGHT = 24
BASE_WIDGET_WIDTH = 80
SMALL_FONT_NAME = "JuliaMono-Bold.ttf"
SMALL_FONT_SIZE = 14
MESSAGE_FONT_SIZE = 14
WIDGETS_MARGIN = 10
BUTTON_WIDTH = BASE_WIDGET_WIDTH
SLIDER_WIDTH = 400
KNOB_SIZE = BASE_WIDGET_HEIGHT
WIDGET_LABEL_SIZE = BUTTON_WIDTH
LED_SIZE = BASE_WIDGET_HEIGHT
WIDGET_LINE = BASE_WIDGET_HEIGHT + WIDGETS_MARGIN
LEFT_COL = WIDGETS_MARGIN * 2 + BUTTON_WIDTH
MED_LABEL_W = (SLIDER_WIDTH / 2) + WIDGETS_MARGIN
BIG_LABEL_W = SLIDER_WIDTH + BUTTON_WIDTH + WIDGETS_MARGIN
VERT_SLIDER_WIDTH = BASE_WIDGET_HEIGHT
VERT_SLIDER_HEIGHT = BASE_WIDGET_WIDTH
MOUSE_LEFT_CLICK = 1
MOUSE_RIGHT_CLICK = 3
MOUSE_WHEEL_UP = 4
MOUSE_WHEEL_DOWN = 5

# Melodic constants
# Durations
THIRTYSECOND = 3
SIXTEENTH = 2 * THIRTYSECOND
DSIXTEENTH = SIXTEENTH * 1.5
EIGHTH = 2 * SIXTEENTH
DEIGHTH = EIGHTH * 1.5
QUARTER = 2 * EIGHTH
TEIGHTH = QUARTER / 3
DQUARTER = QUARTER * 1.5
HALF = 2 * QUARTER
DHALF = HALF * 1.5
FULL = 2 * HALF
BEAT = QUARTER
BAR = FULL
DEFAULT_STRUMMING = 3

# Ponctuation
PONCTUATION_NOT = -1
PONCTUATION_START = 0
PONCTUATION_PART = 1

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
    (-QUARTER, QUARTER, -QUARTER, QUARTER),
    (
        QUARTER,
        QUARTER,
        TEIGHTH,
        TEIGHTH,
        TEIGHTH,
        TEIGHTH,
        TEIGHTH,
        TEIGHTH,
    ),
    (
        TEIGHTH,
        -TEIGHTH,
        TEIGHTH,
        TEIGHTH,
        -TEIGHTH,
        TEIGHTH,
        TEIGHTH,
        -TEIGHTH,
        TEIGHTH,
        TEIGHTH,
        -TEIGHTH,
        TEIGHTH,
    ),
    (DEIGHTH, DEIGHTH, EIGHTH, HALF),
    (QUARTER, QUARTER, EIGHTH, EIGHTH, QUARTER),
    (QUARTER, DQUARTER, EIGHTH, EIGHTH, EIGHTH),
    (EIGHTH, QUARTER, EIGHTH, QUARTER, SIXTEENTH, SIXTEENTH, EIGHTH),
    (EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH),
    (SIXTEENTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, EIGHTH, SIXTEENTH, QUARTER),
    (
        EIGHTH,
        DEIGHTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        EIGHTH,
        DEIGHTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
    ),
    (
        SIXTEENTH,
        SIXTEENTH,
        EIGHTH,
        SIXTEENTH,
        SIXTEENTH,
        EIGHTH,
        SIXTEENTH,
        SIXTEENTH,
        EIGHTH,
        EIGHTH,
        SIXTEENTH,
        SIXTEENTH,
    ),
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
SCALE_NAMES = ["major", "blues", "lydian", "minor"]
# Here the numbers represent semitones from the root
# - 3 is a minor third
# - 4 is a major third
# - ...
SCALES = [
    [0, 2, 4, 5, 7, 9, 11],
    [0, 2, 3, 4, 7, 8],
    [0, 2, 4, 6, 7, 9, 11],
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
(
    ENGINE_TYPE_ARP,
    ENGINE_TYPE_CHORD,
    ENGINE_TYPE_STRUM,
    ENGINE_TYPE_MELOTOR,
    ENGINE_TYPE_MELOSTEP,
) = (
    0,
    1,
    2,
    3,
    4,
)
ENGINE_TYPES = ["arp", "chord", "strum", "melotor", "melostep"]

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
