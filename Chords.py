# -*- coding: utf-8 -*-
import math
import re
import mir_eval
from typing import Union

PITCH_CLASSES = ['C', 'C#', 'D', 'Eb', 'E', 'F',
                 'F#', 'G', 'G#', 'A', 'Bb', 'B']

HARTE_PITCH_CLASSES = [
    ['B#', 'C', 'Dbb'],
    ['B##', 'C#', 'Db'],
    ['C##', 'D', 'Ebb'],
    ['D#', 'Eb', 'Fbb'],
    ['D##', 'E', 'Fb'],
    ['E#', 'F', 'Gbb'],
    ['E##', 'F#', 'Gb'],
    ['F##', 'G', 'Abb'],
    ['G#', 'Ab'],
    ['G##', 'A', 'Bbb'],
    ['A#', 'Bb', 'Cbb'],
    ['A##', 'B', 'Cb']
]

INTERVALS = ['1', 'b2', '2', 'b3', '3', '4', '#4', '5', 'b6', '6', 'b7', '7', '8',
             'b9', '9', 'b10', '10', '11', 'b12', '12', 'b13', '13', '#13']

HARTE_INTERVALS = [
    ['1', 'bb2'], ['#1', 'b2'], ['2', 'bb3'],
    ['#2', 'b3'], ['3', 'b4'], ['#3', '4'],
    ['#4', 'b5'], ['5', 'bb6'], ['#5', 'b6'],
    ['6', 'bb7'], ['#6', 'b7'], ['7', 'b8'],
    ['#7', '8', 'bb9'], ['#8', 'b9'], ['9', 'bb10'],
    ['#9', 'b10'], ['10', 'b11'], ['#10', '11'],
    ['#11', 'b12'], ['12', 'bb13'], ['#12', 'b13'],
    ['13'], ['#13']
]


def find_item(list_containing_list, item):
    """
    Find the index of the list that contains the item
    :param list_containing_list: List of lists; one of them must contain the item
    :param item: The item we are looking for
    :return: Index of the item in the outer list
    >>> find_item([[1,2,3],[4,5,6]],5)
    1
    >>> find_item(HARTE_INTERVALS, 'b13')
    20
    """
    for _list in list_containing_list:
        if item in _list:
            return list_containing_list.index(_list)
    return None


class Pitch:
    def __init__(self, midi_pitch):
        # type: (int) -> None
        """
        Create a Pitch instance based on its MIDI-pitch
        :param midi_pitch: MIDI-pitch, e.g.: MIDI-pitch 69 corresponds with A4 (440 Hz)
        >>> p = Pitch(69)
        >>> p.pitch_class
        'A'
        >>> p.octave_number
        4
        """
        self.midi_pitch = midi_pitch
        self._fix()

    @classmethod
    def from_pitch_class_and_octave_number(cls, pitch_class, octave_number):
        # type: (str, int) -> cls
        """
        Create a Pitch instance based on its pitch class and octave number (e.g. 'A' and 4)
        :param pitch_class: Pitch class string (e.g. 'A')
        :param octave_number: Octave number (e.g. 4)
        :return: Pitch, as specified by the pitch class and octave number
        >>> p = Pitch.from_pitch_class_and_octave_number('A', 4)
        >>> p.midi_pitch
        69
        >>> p.harte_pitch_class
        ['G##', 'A', 'Bbb']
        """
        pitch_class_number = PITCH_CLASSES.index(pitch_class)
        return cls(12 * octave_number + pitch_class_number + 12)

    @classmethod
    def from_pitch_name(cls, pitch_name):
        # type: (str) -> cls
        """
        Create a Pitch instance based on its pitch name (a str consisting of pitch class and octave number (e.g. 'A4')
        Note: works only with single sharp/flats; fails with double sharps/flats
        :param pitch_name: Name, consisting of pitch class and octave number
        :return: Pitch, as specified by its pitch name
        >>> Pitch.from_pitch_name('A4').midi_pitch
        69
        >>> Pitch.from_pitch_name('Bb4').midi_pitch # We can handle single sharps or flats
        70
        >>> Pitch.from_pitch_name('Bbb4')           # We cannot handle double sharps or flats
        Traceback (most recent call last):
        ...
        ValueError: invalid literal for int() with base 10: 'b4'
        """
        if 'b' in pitch_name or '#' in pitch_name:
            return cls.from_pitch_class_and_octave_number(pitch_name[0:2], int(pitch_name[2:]))
        return cls.from_pitch_class_and_octave_number(pitch_name[0], int(pitch_name[1:]))

    def _midi_pitch_to_pitch_class(self):
        """
        Get the pitch class from the midi pitch of our Pitch object
        :return: Pitch class from the midi pitch of our Pitch object
        >>> Pitch(69)._midi_pitch_to_pitch_class()
        'A'
        """
        return PITCH_CLASSES[self.midi_pitch % 12]

    def _midi_pitch_to_harte_class(self):
        """
        Get the harte class from the midi pitch of our Pitch object
        :return: Harte class from the midi pitch of our Pitch object
        >>> Pitch(69)._midi_pitch_to_harte_class()
        ['G##', 'A', 'Bbb']
        """
        return HARTE_PITCH_CLASSES[self.midi_pitch % 12]

    def _midi_pitch_to_octave_number(self):
        """
        Get the octave number from the midi pitch of our Pitch object
        :return: Octave number from the midi pitch of our Pitch object
        >>> Pitch(69)._midi_pitch_to_octave_number()
        4
        """
        return int(math.floor(self.midi_pitch / 12)) - 1

    def _fix(self):
        """
        Make sure that the pitch class, Harte pitch class and octave number correspond to the midi pitch.
        This is a necessary step after creation or transposition of the Pitch.
        """
        self.pitch_class = self._midi_pitch_to_pitch_class()
        self.harte_pitch_class = self._midi_pitch_to_harte_class()
        self.octave_number = self._midi_pitch_to_octave_number()

    @staticmethod
    def is_higher_than(pitch_1, pitch_2):
        # type: (Pitch, Pitch) -> bool
        """
        Checks if pitch 1 is higher than pitch 2
        :param pitch_1: First pitch
        :param pitch_2: Second pitch
        :return: Is pitch 1 higher than pitch 2?
        >>> Pitch.is_higher_than(Pitch.from_pitch_name('A4'), Pitch.from_pitch_name('G5'))
        False
        """
        return pitch_1.midi_pitch > pitch_2.midi_pitch

    def transpose_by(self, interval):
        # type: (Interval) -> None
        """
        Transposes the Pitch up by a certain interval
        :param interval: The Interval with which we transpose our Pitch up
        >>> p = Pitch(69)
        >>> p.transpose_by(Interval.from_harte_interval('b2'))
        >>> p.midi_pitch
        70
        """
        self.midi_pitch = self.midi_pitch + interval.semitone_interval
        self._fix()

    def transpose_down_by(self, interval):
        # type: (Interval) -> None
        """
        Transposes the Pitch down by a certain interval
        :param interval: The Interval with which we transpose our Pitch down
        >>> p = Pitch(69)
        >>> p.transpose_down_by(Interval.from_harte_interval('b2'))
        >>> p.midi_pitch
        68
        """
        self.midi_pitch = self.midi_pitch - interval.semitone_interval
        self._fix()


class PitchClass:
    def __init__(self, pitch_class_number):
        # type: (int) -> None
        """
        Obtain a PitchClass by its pitch class number
        :param pitch_class_number: Number of the pitch class
        >>> str(PitchClass(0))
        'C'
        >>> str(PitchClass(4))
        'E'
        >>> str(PitchClass(11))
        'B'
        >>> PitchClass(2).harte_pitch_class
        ['C##', 'D', 'Ebb']
        """
        self.pitch_class_number = pitch_class_number
        self.harte_pitch_class = HARTE_PITCH_CLASSES[pitch_class_number]

    def __eq__(self, other):
        # type: (PitchClass) -> bool
        """
        Tests if this PitchClass is equal to another PitchClass object
        :param other: The other PitchClass object
        :return: Is this PitchClass equal to the other PitchClass object?
        >>> p = PitchClass.from_harte_pitch_class('D')
        >>> q = PitchClass.from_harte_pitch_class('Ebb')
        >>> r = PitchClass.from_harte_pitch_class('Eb')
        >>> p == q
        True
        >>> q == r
        False
        >>> s = PitchClass(2)
        >>> s == p
        True
        """
        return self.pitch_class_number == other.pitch_class_number

    def __hash__(self):
        # type: () -> int
        """
        Hashes a PitchClass to an int, so we can use it as dictionary index
        :return: Hashed PitchClass
        """
        return hash(self.pitch_class_number)

    def __str__(self):
        # type: () -> str
        """
        Gets an easily readable name for the pitch Class (instead of a list of Harte pitch classes)
        :return: Easily readable name for the pitch Class
        >>> str(PitchClass(1))
        'C#'
        """
        return PITCH_CLASSES[self.pitch_class_number]

    @classmethod
    def from_harte_pitch_class(cls, harte_pitch_class):
        # type: (str) -> cls
        """
        Create a PitchClass object from its Harte pitch class
        :param harte_pitch_class: A string that defines a pitch class with at most two sharps/flats
        :return: PitchClass as specified by the Harte pitch class
        >>> PitchClass.from_harte_pitch_class('Gbb').pitch_class_number
        5
        """
        pitch_class_number = find_item(HARTE_PITCH_CLASSES, harte_pitch_class)
        return cls(pitch_class_number)


class Fingering:
    def __init__(self, base_fret, e2, a2, d3, g3, b3, e4):
        # type: (str, str, str, str, str, str, str) -> None
        """
        Create a fingering: finger positions on a guitar that define the sounding pitches / pitch classes and bass pitch
        :param base_fret: Standard value is '1', can be higher is if the capo is placed on a higher fret
        :param e2: Finger position on the e2 string. Can be either a digit or an 'x'
        :param a2: Finger position on the a2 string. Can be either a digit or an 'x'
        :param d3: Finger position on the d3 string. Can be either a digit or an 'x'
        :param g3: Finger position on the g3 string. Can be either a digit or an 'x'
        :param b3: Finger position on the b3 string. Can be either a digit or an 'x'
        :param e4: Finger position on the e4 string. Can be either a digit or an 'x'
        >>> f = Fingering('1', 'x', '0', '2', '2', '1', '0')
        >>> f.pitch_class_set == ['A', 'C', 'E']
        True
        >>> f.bass_pitch.pitch_class
        'A'
        >>> f.finger_list == ('x', '0', '2', '2', '1', '0')
        True
        """
        self.base_fret = base_fret
        self.finger_list = (e2, a2, d3, g3, b3, e4)
        base_pitches = (39, 44, 49, 54, 58, 63)
        self.pitch_list = []
        self.pitch_class_set = set()

        # Find notes in the Fingering
        for finger_i in range(0, len(self.finger_list)):
            if self.finger_list[finger_i] != 'x':
                # A note is played on this string, this must be a digit representing the finger position
                finger_nr = int(self.finger_list[finger_i])
                pitch = Pitch(base_pitches[finger_i] + int(base_fret) + finger_nr)
                self.pitch_list.append(pitch)
                self.pitch_class_set.add(pitch.pitch_class)
        self.pitch_class_set = sorted(self.pitch_class_set)

        # Find bass notes
        self.bass_pitch = self.pitch_list[0]
        for pitch in self.pitch_list[1:]:
            if Pitch.is_higher_than(self.bass_pitch, pitch):
                self.bass_pitch = pitch

    def __hash__(self):
        # type: () -> int
        """
        Convert the Fingering to a unique integer value, so we can use it as key in a dictionary
        :return: A unique integer value for this Fingering
        """
        return hash((self.base_fret, self.finger_list))

    def __eq__(self, other):
        # type: (Fingering) -> bool
        """
        Checks if this Fingering is equal to another Fingering
        :param other: The other Fingering
        :return: Is this Fingering equal to the other Fingering?
        >>> Fingering('1', 'x', '0', '2', '2', '1', '0') == Fingering('1', 'x', '0', '2', '2', '1', '0')
        True
        >>> # The fingering must be exactly the same, so two versions of the A minor chord may not be equal
        >>> a_minor_1 = Fingering('1', 'x', '0', '2', '2', '1', '0')
        >>> a_minor_2 = Fingering('1', 'x', 'x', 'x', '2', '1', '0')
        >>> a_minor_1.pitch_class_set == a_minor_2.pitch_class_set
        True
        >>> a_minor_1 == a_minor_2
        False
        """
        return self.base_fret == other.base_fret and self.finger_list == other.finger_list

    def get_extended_chroma_vector(self):
        # type: () -> list
        """
        Transforms the Fingering into a list in which the first 12 elements correspond with the 12 pitch classes and the
        final element is the bass class pitch class
        :return: 13D chroma-like vector with bass pitch class information
        >>> f = Fingering('1', 'x', '0', '2', '2', '1', '0')
        >>> f.get_extended_chroma_vector()
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 9]
        """
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for pitch_class in self.pitch_class_set:
            result[PITCH_CLASSES.index(pitch_class)] = 1
        result.append(self.bass_pitch.midi_pitch % 12)
        return result


class Interval:
    def __init__(self, semitone_interval):
        # type: (int) -> None
        """
        Create an interval based on the distance in semitones.
        :param semitone_interval: Distance in semitones
        >>> str(Interval(0)) #  Prime
        '1'
        >>> str(Interval(8)) #  Minor sixth
        'b6'
        >>> Interval(6).harte_interval #  Tritone, can be a augmented fourth and a diminished fifth
        ['#4', 'b5']
        """
        self.semitone_interval = semitone_interval
        self.harte_interval = HARTE_INTERVALS[semitone_interval]

    def __eq__(self, other):
        # type: (Interval) -> bool
        """
        Check if two intervals sound the same (although they may be called by different Harte labels)
        :param other: The other interval
        :return: Do two intervals soud the same?
        >>> Interval.from_harte_interval('#4') == Interval.from_harte_interval('b5')
        True
        """
        return self.semitone_interval == other.semitone_interval

    def __hash__(self):
        # type: () -> int
        """
        Get a unique integer that identifies this Interval
        :return: Unique integer that identifies this Interval
        """
        return hash(self.semitone_interval)

    def __lt__(self, other):
        # type: (Interval) -> bool
        """
        Checks if this interval is smaller than the other Interval
        :param other: The other Interval
        :return: Is this interval smaller than the other Interval?
        >>> Interval.from_harte_interval('b3') < Interval.from_harte_interval('3')
        True
        >>> Interval(0) < Interval(0)
        False
        """
        return self.semitone_interval < other.semitone_interval

    def __str__(self):
        # type: () -> str
        """
        Convert the Interval to an easily readable string (the most common interval name)
        :return: The most common interval name
        >>> str(Interval(0)) == '1'
        True
        >>> str(Interval(0)) == 'bb2'
        False
        """
        return INTERVALS[self.semitone_interval]

    @classmethod
    def from_harte_interval(cls, harte_interval_string):
        # type: (Union(int, str)) -> cls
        """
        Create an interval from a Harte interval
        :param harte_interval_string: String (or int) that identifies the interval
        :return: Interval as defined by the Harte interval
        >>> Interval(0) == Interval.from_harte_interval('bb2')
        True
        >>> Interval.from_harte_interval('1') == Interval.from_harte_interval('bb2')
        True
        """
        if isinstance(harte_interval_string, int):
            harte_interval_string = str(harte_interval_string)
        harte_interval_string = harte_interval_string.strip(' ')
        return cls(find_item(HARTE_INTERVALS, harte_interval_string))

    @classmethod
    def from_pitch_class_distances(cls, from_pitch_class, to_pitch_class):
        # type: (PitchClass, PitchClass) -> cls
        """
        Create an Interval by the distance between the pitch classes, wrapping around the octave
        :param from_pitch_class: Pitch class of start of Interval
        :param to_pitch_class: Pitch class of end of Interval
        :return: Interval between two pitch classes
        >>> a = PitchClass.from_harte_pitch_class('A')
        >>> c_sharp = PitchClass.from_harte_pitch_class('C#')
        >>> str(Interval.from_pitch_class_distances(a, c_sharp))
        '3'
        """
        semitone_interval = to_pitch_class.pitch_class_number - from_pitch_class.pitch_class_number
        if semitone_interval < 0:
            semitone_interval += 12
        return cls(semitone_interval)


class Chord:
    def __init__(self, root_note, components_degree_list, bass_degree):
        # type: (PitchClass, list[Interval], Interval) -> None
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
        # type: (Chord) -> bool
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
        return self.root_note == other.root_note and \
               self.components_degree_list == other.components_degree_list and \
               self.bass_degree == other.bass_degree

    def __hash__(self):
        # type: () -> int
        """
        Hashes the chord to a unique integer, so we can use Chords as keys in a dictionary or set
        :return: Unique integer for this chord
        """
        return hash((self.root_note, self.bass_degree, self.components_degree_list))

    def __str__(self):
        # type: () -> str
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
        # type: (str) -> list[str]
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
        # type: (str) -> Union(list[str], None)
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
        # type: (PitchClass, str, list[str], Interval, str) -> cls
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
        # type: (str) -> cls
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
        # type: (str) -> cls
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
