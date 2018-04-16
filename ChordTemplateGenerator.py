# -*- coding: utf-8 -*-
CHORD_TEMPLATES_MAJOR_MINOR = [
    ('', [0, 4, 7]),
    ('m', [0, 3, 7]),
]

CHORD_TEMPLATES_SEVENTHS = [
    ('7', [0, 4, 7, 10]),
    ('maj7', [0, 4, 7, 11]),
    ('m7', [0, 3, 7, 10])
]

CHORD_TEMPLATES_OTHER = [
    ('dim', [0, 3, 6]),
    ('aug', [0, 4, 8]),
    ('sus2', [0, 2, 7]),
    ('sus4', [0, 5, 7]),
    ('6', [0, 4, 7, 9]),
    ('m6', [0, 3, 7, 9]),
    ('6/9', [0, 2, 4, 7, 9]),
    ('5', [0, 7]),
    ('9', [0, 2, 4, 7, 10]),
    ('m9', [0, 2, 3, 7, 10]),
    ('maj9', [0, 2, 4, 7, 11]),
    ('11', [0, 2, 4, 5, 7, 10]),
    ('13', [0, 2, 4, 5, 7, 9, 10]),
    ('add9', [0, 2, 4, 7]),             # Also: add2
    ('7-5', [0, 4, 6, 10]),
    ('7+5', [0, 4, 8, 10])
]


def _generate_chroma(chord_template_list):
    result = []
    for chord_template in chord_template_list:
        for key_note in range(0, 12):
            chroma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for note_index in chord_template[1]:
                chroma[(note_index + key_note) % 12] = 1
            result.append([key_note, chord_template[0], chroma])
    return result


def generate_chroma_major_minor():
    return _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR)


def generate_chroma_major_minor_sevenths():
    return _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR + CHORD_TEMPLATES_SEVENTHS)


def generate_chroma_all_chords():
    return _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR + CHORD_TEMPLATES_SEVENTHS + CHORD_TEMPLATES_OTHER)
