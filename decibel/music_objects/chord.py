import re

import mir_eval

from decibel.music_objects.interval import Interval
from decibel.music_objects.pitch_class import PitchClass


class Chord:
    def __init__(self, root_note, components_degree_list, bass_degree):
        """
        Creates a chord, which can be uniquely defined by its root note, component degrees and bass degree

        :param root_note: Pitch class of the root note
        :param components_degree_list: List of Intervals that are in the chord
        :param bass_degree: Interval from root to bass note
        """
        self.root_note = root_note
        self.bass_degree = bass_degree
        self.components_degree_list = sorted(components_degree_list)

    def __eq__(self, other):
        """
        Checks if this chord sounds the same as another chord (which may be a No-Chord)

        :param other: The other chord
        :return: Is this chord equal to the other chord?

        >>> c1 = Chord.from_harte_chord_string("D#:min7")
        >>> c2 = Chord.from_harte_chord_string("Eb:(b3,5,b7)")
        >>> c1 == c2
        True
        """
        if self is None and other is None:
            return True
        if self is None or other is None:
            return False
        return self.root_note == other.root_note and self.components_degree_list == other.components_degree_list and \
            self.bass_degree == other.bass_degree

    def __hash__(self):
        """
        Hashes the chord to a unique integer, so we can use Chords as keys in a dictionary or set

        :return: Unique integer for this chord
        """
        return hash((self.root_note, self.bass_degree, self.components_degree_list))

    def __str__(self):
        """
        Convert the Chord to a string, using shorthands when possible

        :return: String representation of a chord, using shorthand when possible

        >>> str(Chord.from_harte_chord_string('Db:(3, 5)'))
        'C#'
        >>> str(Chord.from_harte_chord_string('E:(b3, 5)'))
        'E:min'
        >>> str(Chord.from_harte_chord_string('Gb:(#2, 5, b7)'))
        'F#:min7'
        >>> str(Chord.from_harte_chord_string('C:(3,5,7)'))
        'C:maj7'
        >>> str(Chord.from_harte_chord_string('B:7'))
        'B:7'
        >>> str(Chord.from_harte_chord_string('C:(1, 2, 3,4,5,6,7)'))
        'C:(1,2,3,4,5,6,7)'
        """
        components = []
        for component in self.components_degree_list:
            components.append(str(component))
        if sorted(components) == sorted(['b3', '5']):
            chord_string = mir_eval.chord.join(str(self.root_note), 'min', [], str(self.bass_degree))
        elif sorted(components) == sorted(['3', '5']):
            chord_string = mir_eval.chord.join(str(self.root_note), '', [], str(self.bass_degree))
        elif sorted(components) == sorted(['b3', '5', 'b7']):
            chord_string = mir_eval.chord.join(str(self.root_note), 'min7', [], str(self.bass_degree))
        elif sorted(components) == sorted(['3', '5', '7']):
            chord_string = mir_eval.chord.join(str(self.root_note), 'maj7', [], str(self.bass_degree))
        elif sorted(components) == sorted(['3', '5', 'b7']):
            chord_string = mir_eval.chord.join(str(self.root_note), '7', [], str(self.bass_degree))
        else:
            chord_string = mir_eval.chord.join(str(self.root_note), '', components, str(self.bass_degree))
        return chord_string

    @staticmethod
    def _component_list_from_common_tab_shorthand(shorthand_string):
        """
        Given a tab shorthand string, return the component list (or the empty list if the string was not a shorthand)

        :param shorthand_string: Shorthand of a chord mode, that typically appears in tabs
        :return: Component list belonging to the shorthand

        >>> Chord._component_list_from_common_tab_shorthand('7')
        ['3', '5', 'b7']
        >>> Chord._component_list_from_common_tab_shorthand('i_am_not_really_a_shorthand_and_not_short_either')
        []
        """
        shorthands = ['7sus4', '7sus', 'sus2', 'sus4', 'sus', 'm6', '6/9', '6', '7-5', '7\+5', '5', 'm9', 'maj9',
                      'add9', '9', '11', '13', 'maj7', 'M7', 'maj', 'min7', 'm7', 'm', 'dim', 'aug', '+', '7']
        component_lists = [['4', '5', 'b7'], ['4', '5', 'b7'], ['2', '5'], ['4', '5'], ['4', '5'],
                           ['b3', '5', '6'], ['2', '3', '5', '6'], ['3', '5', '6'], ['3', 'b5', 'b7'],
                           ['3', '#5', 'b7'], ['5'], ['2', 'b3', '5', 'b7'], ['2', '3', '5', '7'],
                           ['2', '3', '5'], ['2', '3', '5', 'b7'], ['2', '3', '4', '5', 'b7'],
                           ['2', '3', '4', '5', '6', 'b7'], ['3', '5', '7'], ['3', '5', '7'], ['3', '5'],
                           ['b3', '5', 'b7'], ['b3', '5', 'b7'], ['b3', '5'], ['b3', 'b5'], ['3', '#5'],
                           ['3', '#5'], ['3', '5', 'b7']]
        if shorthand_string not in shorthands:
            return []
        return component_lists[shorthands.index(shorthand_string)]

    @staticmethod
    def _component_list_from_harte_shorthand(shorthand_string):
        """
        Given a harte shorthand string, return the component list (or None if the string was not a shorthand)

        :param shorthand_string: Shorthand of a chord mode, that typically appears in chord label files
        :return: Component list belonging to the shorthand

        >>> Chord._component_list_from_harte_shorthand('7')
        ['3', '5', 'b7']
        >>> Chord._component_list_from_harte_shorthand('i_am_not_really_a_shorthand_and_not_short_either')
        """
        shorthands = ['maj', 'min', 'dim', 'aug',
                      'maj7', 'min7', '7', 'dim7', 'hdim7', 'minmaj7',
                      'maj6', 'min6', '9', 'maj9', 'min9', 'sus4', '']
        component_lists = [['3', '5'], ['b3', '5'], ['b3', 'b5'], ['3', '#5'],
                           ['3', '5', '7'], ['b3', '5', 'b7'], ['3', '5', 'b7'],
                           ['b3', 'b5', 'bb7'], ['b3', 'b5', 'b7'], ['b3', '5', '7'],
                           ['3', '5', '6'], ['b3', '5', '6'], ['3', '5', 'b7', '9'],
                           ['3', '5', '7', '9'], ['b3', '5', 'b7', '9'], ['4', '5'], []]
        if shorthand_string not in shorthands:
            return None
        return component_lists[shorthands.index(shorthand_string)]

    @classmethod
    def from_shorthand_degree_bass(cls, root_note, shorthand_string, degree_string_list, bass_degree,
                                   shorthand_type='harte'):
        """
        Create a chord from a root note, shorthand string, degree string list, bass degree and optional shorthand type

        :param root_note: Root note of the chord
        :param shorthand_string: Shorthand string that specifies the degrees (may be empty)
        :param degree_string_list: List of degrees. A degree starting with * means that this degree is not in the chord
        :param bass_degree: Bass degree Interval
        :param shorthand_type: String that specifies the shorthand type: either 'harte' or 'tab'
        :return: Chord as specified by the root note, shorthand, degrees and bass

        >>> str(Chord.from_shorthand_degree_bass(PitchClass(0), 'min7', ['*b7'], Interval.from_harte_interval('b3')))
        'C:min/b3'
        """
        # Start with the standard degrees for this shorthand
        if shorthand_type == 'harte':
            component_list = Chord._component_list_from_harte_shorthand(shorthand_string)
        elif shorthand_type == 'tab':
            component_list = Chord._component_list_from_common_tab_shorthand(shorthand_string)
        else:
            something_went_wrong_here = True
            component_list = []

        # Add or remove degrees from the degree_string_list
        for degree in degree_string_list:
            if degree[0] == '*':
                if degree[1:] in component_list:
                    # This degree is not in the chord
                    component_list.remove(degree[1:])
            else:
                # This degree must be added to the chord
                component_list.append(degree)

        # Remove duplicates
        component_list = list(set(component_list))

        # Convert all degrees to Intervals
        component_degree_list = []
        for component in component_list:
            component_degree_list.append(Interval.from_harte_interval(component))

        return cls(root_note, component_degree_list, bass_degree)

    @classmethod
    def from_harte_chord_string(cls, chord_string):
        """
        Create a chord from a chord string in the syntax proposed in the 2005 paper 'SYMBOLIC REPRESENTATION OF
        MUSICAL CHORDS: A PROPOSED SYNTAX FOR TEXT ANNOTATIONS' by Harte et al.

        :param chord_string: Chord string in syntax proposed by Harte et al.
        :return: Chord type as specified by the chord string

        >>> Chord.from_harte_chord_string('C') == Chord.from_harte_chord_string('C:(3,5)')
        True
        >>> Chord.from_harte_chord_string('C:maj(4)') == Chord.from_harte_chord_string('C:(3,4,5)')
        True
        """
        # First find non-chord strings
        if chord_string == 'N':
            return None

        # Extract root, shorthand, degree_list and bass_degree from the chord string
        match_chord_string = re.search(
            r'(?P<root>[ABCDEFG][b#]{0,2}):?'
            r'(?P<shorthand>minmaj7|hdim7|maj7|min7|dim7|maj6|min6|maj9|min9|sus9|7|9|maj|min|dim|aug)?'
            r'(\((?P<degree_list>\*?[#b]{0,2}[0-9]{1,2}(, ?\*?[#b]{0,2}[0-9]{1,2})*)\))?'
            r'(/(?P<bass_degree>[#b]{0,2}[0-9]{1,2}))?',
            chord_string
        )

        # Any chord string needs to have a root note
        if match_chord_string.group('root') is None:
            return None
        root_note_pitch_class = PitchClass.from_harte_pitch_class(match_chord_string.group('root'))

        # Find the shorthand
        if match_chord_string.group('shorthand') is None:
            if match_chord_string.group('degree_list') is None:
                # This is a major chord
                shorthand_str = 'maj'
            else:
                # The chord type is specified by the degree list
                shorthand_str = ''
        else:
            # We use a predefined shorthand
            shorthand_str = match_chord_string.group('shorthand')

        # Find the degrees
        if match_chord_string.group('degree_list') is None:
            degree_str_list = []
        else:
            degree_str_list = match_chord_string.group('degree_list').split(',')

        # Find the bass degree
        if match_chord_string.group('bass_degree') is None:
            bass_degree = Interval(0)
        else:
            bass_degree = Interval.from_harte_interval(match_chord_string.group('bass_degree'))

        # Return the chord
        return cls.from_shorthand_degree_bass(root_note_pitch_class, shorthand_str, degree_str_list, bass_degree)

    @classmethod
    def from_common_tab_notation_string(cls, chord_string):
        """
        Create a chord from a string as it is typically found in a tab file

        :param chord_string: Chord string as you typically find it in a tab file
        :return: Chord as specified by the chord string

        >>> str(Chord.from_common_tab_notation_string('C:min'))
        'None'
        >>> str(Chord.from_common_tab_notation_string('Cmaj'))
        'C'
        >>> str(Chord.from_common_tab_notation_string('Db11'))
        'C#:(2,3,4,5,b7)'
        """
        chord_parts = re.search(
            r'(?P<root_str>[ABCDEFG][b#]?)'
            r'(?P<chord_type_str>7sus4|7sus|sus2|sus4|sus|m6|6/9|6|7-5|7\+5|5|m9|maj9|add9|9|11|13|maj7|M7|maj|min7|m7'
            r'|m|dim|aug|\+|7)?'
            r'(/(?P<bass_note_str>[ABCDEFG][b#])?)?$',
            chord_string)

        # This string was not recognized as a chord
        if chord_parts is None:
            return None

        # Root note
        root_note_pitch_class = PitchClass.from_harte_pitch_class(chord_parts.group('root_str'))

        # Chord type
        chord_type_string = chord_parts.group('chord_type_str')
        if chord_type_string is None:
            chord_type_string = 'maj'

        # Bass note
        bass_note_string = chord_parts.group('bass_note_str')
        if bass_note_string is None:
            bass_interval = Interval(0)
        else:
            bass_note_pitch_class = PitchClass.from_harte_pitch_class(bass_note_string)
            bass_interval = Interval.from_pitch_class_distances(root_note_pitch_class, bass_note_pitch_class)

        return Chord.from_shorthand_degree_bass(root_note_pitch_class, chord_type_string, [], bass_interval, 'tab')