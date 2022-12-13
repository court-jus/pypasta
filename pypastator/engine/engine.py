import math
import random
from presets import SCALES, CHORDS


def get_candidate_notes(
    related_to,
    scale,
    chord_type,
    chord,
):
    scale_scheme = SCALES[scale]
    if related_to in ("chord", "invchord"):
        result = []
        for note_degree in CHORDS[chord_type]:
            target_note = note_degree - 1 + (chord - 1)
            if related_to == "chord":
                result.append(
                    scale_scheme[target_note % len(scale_scheme)]
                    + 12 * math.floor(target_note / len(scale_scheme))
                )
            result.append(scale_scheme[target_note % len(scale_scheme)])
        return result
    else:
        return scale_scheme


def get_notes(song, notes, octaves, related_to):
    if related_to == "static":
        return notes
    candidate_notes = get_candidate_notes(
        related_to, song.scale, song.current_chord_type, song.current_chord
    )
    result = []
    for octave in octaves:
        for required_note in notes:
            rotated = required_note % 10
            octave_shift = math.floor(required_note / 10)
            if len(candidate_notes) > rotated:
                result.append(
                    song.root_note
                    + 12 * (octave + octave_shift)
                    + candidate_notes[rotated % len(candidate_notes)]
                    + 12 * math.floor(rotated / len(candidate_notes))
                )
    if related_to == "invchord":
        return sorted(result)
    return result


def compute_melotor(melotor, position, base_division, song_data):
    if (
        len(melotor.current_melo) > 0
        and position % (melotor.melo_change_div / base_division) != 0
    ):
        return
    chord_notes = [
        (val - 1 + song_data.current_chord - 1) % 7
        for val in CHORDS[song_data.current_chord_type]
    ]
    available_notes = [0, 1, 2, 3, 4, 5, 6]
    # TODO: read that from Song Data
    indexed_probabilities = {}
    for idx, note in enumerate(available_notes):
        is_in_chord = 1 if note in chord_notes else 0
        proba = math.floor(
            ((melotor.notes_probabilities[idx] or 0) / 100)
            * (100 - melotor.chord_influence)
            + is_in_chord * melotor.chord_influence
        )
        indexed_probabilities[note] = proba
    ponderated_notes = [[note] * proba for note, proba in indexed_probabilities.items()]
    if not ponderated_notes:
        ponderated_notes = [0]

    melo = melotor.current_melo[0 : melotor.melo_length]
    if melo.length < melotor.melo_length:
        # Add notes to fill the melo
        while melo.length < melotor.melo_length:
            melo.append(random.choice(ponderated_notes))
    else:
        # Change some notes
        change_candidates = []
        for idx, note in enumerate(melotor.current_melo):
            change_candidates.extend(
                [idx] * math.max(100 - indexed_probabilities[note], 1)
            )
        how_many_to_change = math.ceil(
            melotor.melo_change_strength / 100 * melotor.melo_length
        )
        while how_many_to_change > 0:
            chosen_idx = random.choice(change_candidates)
            melo[chosen_idx] = random.choice(ponderated_notes)
            change_candidates = [val for val in change_candidates if val != chosen_idx]
            howManyToChange -= 1
    return melo


def compute_melo_step(melostep, position, division, song):
    result = []
    for idx, curr in enumerate(melostep.input):
        if curr == "*" or len(result) == 0:
            result.append(0)
        prev_val = result[-1]
        if curr == " " or curr == "_":
            result.append(prev_val)
        if curr == "u":
            result.append(prev_val + 1)
        if curr == "d":
            result.append((prev_val - 1) % (len(SCALES[song.scale]) - 1))
        if curr == "U":
            result.append(prev_val + 2)
        if curr == "D":
            result.append((prev_val - 2) % (len(SCALES[song.scale]) - 1))
    return result


def compute_euclidean_value(x, density, grid_size, mode):
    if mode == "sinus":
        # x is between 0 and gridSize
        # newX is between 0 and 2*PI and relates to density
        new_x = ((x / grid_size) * math.pi * 2 * (64 - density)) / 32
        return math.floor(((math.cos(new_x) + 1) * grid_size) / 8 + grid_size / 6)
    if mode == "dexp":
        slope = 1
        new_x = (((x + 1) / density) * 4.16) / 6
        y = math.floor(math.exp(new_x) * slope)
        return y
    if mode == "uexp":
        slope = 1
        new_x = (((64 - x + 1) / density) * 4.16) / 6
        y = math.floor(math.exp(new_x) * slope)
        return y
    # Default: linear
    return math.floor(((x + 1) * (64 - density)) / grid_size) + 1


def compute_euclidean(x, y, density, grid_size, mode):
    if density == 0:
        return
    new_y = None if y is None else grid_size - y
    new_x = x % grid_size
    x_prev = (new_x - 1) % grid_size
    new_value = compute_euclidean_value(new_x, density, grid_size, mode)
    if new_y is not None and new_value != new_y:
        return
    prev_value = compute_euclidean_value(x_prev, density, grid_size, mode)
    if prev_value != new_value:
        return 0
    return 1


def get_available_notes(track, song):
    track.recompute_melo(song)
    candidate_notes = get_notes(
        song, track.availableDegrees, track.octaves, track.relatedTo
    )
    if track.relatedTo == "static":
        return candidate_notes
    [low_limit, high_limit] = track.getNotesLimits()
    [low_candidate, high_candidate] = [
        math.min(candidate_notes),
        math.max(candidate_notes),
    ]
    candidates_center = math.floor((high_candidate - low_candidate) / 2) + low_candidate
    shift = math.floor((track.gravity_center - candidates_center) / 12) * 12
    shifted = (
        [note + shift for note in candidate_notes]
        if track.related_to == "chord"
        else candidate_notes
    )
    result = []
    for note in shifted:
        if note < low_limit:
            # FIXME, there's probably a bug here,
            # 'note' does not influence the final result
            transp = low_limit - note
            result.append(note + transp + (12 - (transp % 12)))
        elif note > high_limit:
            # FIXME, there's probably a bug here,
            # 'note' does not influence the final result
            transp = note - high_limit
            result.append(note - transp - (12 - (transp % 12)))
        else:
            result.append(note)
    return result
