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
    # type: ((str, list[int])) -> list[(int, str, list[int])]
    """
    Generate a list of chord templates (key-mode-chroma tuples), based on the chord template list.
    :param chord_template_list: list of names and intervals forming chords
    :return: List of chord templates: (key, mode-str, chroma-list) tuples
    >>> _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR)[0]
    [0, '', [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]]
    >>> _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR)[23]
    [11, 'm', [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1]]
    """
    result = []
    for chord_template in chord_template_list:
        for key_note in range(0, 12):
            chroma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for note_index in chord_template[1]:
                chroma[(note_index + key_note) % 12] = 1
            result.append([key_note, chord_template[0], chroma])
    return result


def generate_chroma_major_minor():
    """
    Generate a list of major and minor chord templates
    :return: List of chord templates: (key, mode-str, chroma-list) tuples
    """
    return _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR)


def generate_chroma_major_minor_sevenths():
    """
    Generate a list of major, minor and sevenths chord templates
    :return: List of chord templates: (key, mode-str, chroma-list) tuples
    """
    return _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR + CHORD_TEMPLATES_SEVENTHS)


def generate_chroma_all_chords():
    """
    Generate a list of all kinds of chord templates
    :return: List of chord templates: (key, mode-str, chroma-list) tuples
    """
    return _generate_chroma(CHORD_TEMPLATES_MAJOR_MINOR + CHORD_TEMPLATES_SEVENTHS + CHORD_TEMPLATES_OTHER)
