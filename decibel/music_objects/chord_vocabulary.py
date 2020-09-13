# -*- coding: utf-8 -*-
from decibel.music_objects.chord_template import ChordTemplate

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


class ChordVocabulary:
    def __init__(self, name: str, chord_template_list: [(str, [int])]):
        """
        Generate a list of chord templates, based on the chord chord_template list.
        :param name: name of chord vocabulary
        :param chord_template_list: list of names and intervals forming chords
        :return: List of chord templates
        >>> chord_vocabulary = ChordVocabulary(CHORD_TEMPLATES_MAJOR_MINOR)
        >>> chord_template = chord_vocabulary.chord_templates[0]
        >>> chord_template.key
        0
        >>> chord_template.mode
        ''
        >>> chord_template.chroma_list
        [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        >>> chord_vocabulary = ChordVocabulary(CHORD_TEMPLATES_MAJOR_MINOR)
        >>> chord_template = chord_vocabulary.chord_templates[23]
        >>> chord_template.key
        11
        >>> chord_template.mode
        'm'
        >>> chord_template.chroma_list
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        """
        self.name = name
        self.chord_templates = []
        for chord_template in chord_template_list:
            for key_note in range(0, 12):
                chroma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                for note_index in chord_template[1]:
                    chroma[(note_index + key_note) % 12] = 1
                self.chord_templates.append(ChordTemplate(key_note, chord_template[0], chroma))

    @classmethod
    def generate_chroma_major_minor(cls):
        """
        Generate a list of major and minor chord templates
        :return: List of chord templates
        """
        return cls('MajMin', CHORD_TEMPLATES_MAJOR_MINOR)

    @classmethod
    def generate_chroma_major_minor_sevenths(cls):
        """
        Generate a list of major, minor and sevenths chord templates
        :return: List of chord templates
        """
        return cls('Sevenths', CHORD_TEMPLATES_MAJOR_MINOR + CHORD_TEMPLATES_SEVENTHS)

    @classmethod
    def generate_chroma_all_chords(cls):
        """
        Generate a list of all kinds of chord templates
        :return: List of chord templates
        """
        return cls('All', CHORD_TEMPLATES_MAJOR_MINOR + CHORD_TEMPLATES_SEVENTHS + CHORD_TEMPLATES_OTHER)
