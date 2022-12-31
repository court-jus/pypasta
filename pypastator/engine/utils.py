"""
Various util functions.
"""


from pypastator.constants import (
    BAR,
    EIGHTH,
    FULL,
    HALF,
    QUARTER,
    SIXTEENTH,
    THIRTYSECOND,
)


def int_to_roman(num, lowercase=False):
    """
    Convert an integer to roman numerals.
    """
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    if lowercase:
        return roman_num.lower()
    return roman_num


def duration_to_str(duration):
    """
    Convert a duration to its text.

    For example, 96 => 1 bar
    48 => half-note
    ...
    """
    if duration == 0:
        return "∅"
    if duration % BAR == 0:
        bars = duration // BAR
        if bars > 1:
            return f"{bars} bars"
    raw_durations = {
        THIRTYSECOND: "32d",
        SIXTEENTH: "16th",
        EIGHTH: "8th",
        QUARTER: "4th",
        HALF: "½",
        FULL: "1",
    }
    if duration in raw_durations:
        return raw_durations[duration]
    dotted = int(duration * 2 / 3)
    if dotted in raw_durations:
        return f"{raw_durations[dotted]}."
    return str(duration)


def spread_notes(notes, lowest, highest, centered=True):
    """
    Spread given notes in the allowed tessitura.
    """
    current_lowest = min(notes)
    current_highest = max(notes)
    shifted_notes = [
        (
            (note - current_lowest)
            / max(1, (current_highest - current_lowest))
            * (highest - lowest)
        )
        + (lowest if centered else 0)
        for note in notes
    ]
    transposed = []
    for idx, note in enumerate(notes):
        octave = (shifted_notes[idx] - (current_lowest if centered else 0)) // 12
        transposed_note = int(note + octave * 12)
        if transposed_note < lowest:
            transposed_note += (((lowest - transposed_note) // 12) + 1) * 12
        if transposed_note > highest:
            transposed_note -= (((transposed_note - highest) // 12) + 1) * 12
        if transposed_note < lowest:
            # transposed_note is outside of our tessitura, find the closest equivalent
            if lowest - transposed_note > (transposed_note + 12 - lowest):
                transposed_note += 12
        transposed.append(transposed_note)
    return transposed
