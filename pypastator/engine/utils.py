"""
Various util functions.
"""


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


def spread_notes(notes, lowest, highest):
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
        + lowest
        for note in notes
    ]
    transposed = []
    for idx, note in enumerate(notes):
        should_shift_by = (shifted_notes[idx] - note) / 12
        transposed_note = note + round(should_shift_by) * 12
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
