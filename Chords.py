# -*- coding: utf-8 -*-
import math
import re
import mir_eval

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
    for _list in list_containing_list:
        if item in _list:
            return list_containing_list.index(_list)
    return None


class Pitch:
    def __init__(self, midi_pitch):
        if not isinstance(midi_pitch, int):
            raise Exception('Wrong type')
        self.midi_pitch = midi_pitch
        self._fix()

    @classmethod
    def from_pitch_class_and_octave_number(cls, pitch_class, octave_number):
        if not isinstance(pitch_class, str) or not isinstance(octave_number, int):
            raise Exception('Wrong type')
        pitch_class_number = PITCH_CLASSES.index(pitch_class)
        return cls(12 * octave_number + pitch_class_number + 12)

    @classmethod
    def from_pitch_name(cls, pitch_name):
        if not isinstance(pitch_name, str):
            raise Exception('Wrong type')
        if 'b' in pitch_name or '#' in pitch_name:
            return cls.from_pitch_class_and_octave_number(pitch_name[0:2], int(pitch_name[2:]))
        return cls.from_pitch_class_and_octave_number(pitch_name[0], int(pitch_name[1:]))

    def _midi_pitch_to_pitch_class(self):
        return PITCH_CLASSES[self.midi_pitch % 12]

    def _midi_pitch_to_harte_class(self):
        return HARTE_PITCH_CLASSES[self.midi_pitch % 12]

    def _midi_pitch_to_octave_number(self):
        return int(math.floor(self.midi_pitch / 12)) - 1

    def _midi_pitch_to_pitch_name(self):
        return self.pitch_class + str(self.octave_number)

    def _fix(self):
        self.pitch_class = self._midi_pitch_to_pitch_class()
        self.harte_pitch_class = self._midi_pitch_to_harte_class()
        self.octave_number = self._midi_pitch_to_octave_number()

    @staticmethod
    def is_higher_than(pitch_1, pitch_2):
        return pitch_1.midi_pitch > pitch_2.midi_pitch

    def transpose_by(self, interval):
        self.midi_pitch = self.midi_pitch + interval.semitone_interval
        self._fix()

    def transpose_down_by(self, interval):
        self.midi_pitch = self.midi_pitch - interval.semitone_interval
        self._fix()


class PitchClass:
    def __init__(self, pitch_class_number):
        if not isinstance(pitch_class_number, int):
            raise Exception('Wrong type')
        self.pitch_class_number = pitch_class_number
        self.harte_pitch_class = HARTE_PITCH_CLASSES[pitch_class_number]

    def __eq__(self, other):
        return self.pitch_class_number == other.pitch_class_number

    def __hash__(self):
        return hash(self.pitch_class_number)

    def __str__(self):
        return PITCH_CLASSES[self.pitch_class_number]

    @classmethod
    def from_harte_pitch_class(cls, harte_pitch_class):
        if not isinstance(harte_pitch_class, str):
            raise Exception('Wrong type')
        pitch_class_number = find_item(HARTE_PITCH_CLASSES, harte_pitch_class)
        return cls(pitch_class_number)


class Fingering:
    def __init__(self, base_fret, e2, a2, d3, g3, b3, e4):
        self.base_fret = base_fret
        self.finger_list = (e2, a2, d3, g3, b3, e4)
        base_pitches = (39, 44, 49, 54, 58, 63)
        self.pitch_list = []
        self.pitch_class_set = set()
        # Find notes
        for finger_i in range(0, len(self.finger_list)):
            if self.finger_list[finger_i] != 'x':
                fingernr = int(self.finger_list[finger_i])
                pitch = Pitch(base_pitches[finger_i] + int(base_fret) + fingernr)
                self.pitch_list.append(pitch)
                self.pitch_class_set.add(pitch.pitch_class)
        self.pitch_class_set = sorted(self.pitch_class_set)
        # Find bass notes
        self.bass = self.pitch_list[0]
        for pitch in self.pitch_list[1:]:
            if Pitch.is_higher_than(self.bass, pitch):
                self.bass = pitch

    def __hash__(self):
        return hash((self.base_fret, self.finger_list))

    def __eq__(self, other):
        return self.base_fret == other.base_fret and self.finger_list == other.finger_list

    def get_extended_chroma_vector(self):
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for pitch_class in self.pitch_class_set:
            result[PITCH_CLASSES.index(pitch_class)] = 1
        result.append(self.bass.midi_pitch % 12)
        return result


class Interval:
    def __init__(self, semitone_interval):
        if not isinstance(semitone_interval, int):
            raise Exception('Wrong type' + str(semitone_interval))
        self.semitone_interval = semitone_interval
        self.harte_interval = HARTE_INTERVALS[semitone_interval]

    def __eq__(self, other):
        return self.semitone_interval == other.semitone_interval

    def __hash__(self):
        return hash(self.semitone_interval)

    def __lt__(self, other):
        return self.semitone_interval < other.semitone_interval

    def __str__(self):
        return str(self.semitone_interval)

    @classmethod
    def from_harte_interval(cls, harte_interval_string):
        if isinstance(harte_interval_string, int):
            harte_interval_string = str(harte_interval_string)
        if not isinstance(harte_interval_string, str):
            raise Exception('Wrong type')
        return cls(find_item(HARTE_INTERVALS, harte_interval_string))

    @classmethod
    def from_pitch_class_distances(cls, from_pitch_class, to_pitch_class):
        assert isinstance(from_pitch_class, PitchClass)
        assert isinstance(to_pitch_class, PitchClass)

        # Calculate the distance between notes, wrap around the octave
        semitone_interval = to_pitch_class.pitch_class_number - from_pitch_class.pitch_class_number
        if semitone_interval < 0:
            semitone_interval += 12

        return cls(semitone_interval)


class Chord:
    def __init__(self, root_note, components_degree_list, bass_degree):
        if not (isinstance(root_note, PitchClass) and
                isinstance(components_degree_list, list) and
                isinstance(bass_degree, Interval)):
            raise Exception('Wrong type')
        self.root_note = root_note
        self.bass_degree = bass_degree
        self.components_degree_list = sorted(components_degree_list)

    def __eq__(self, other):
        if self is None and other is None:
            return True
        if self is None or other is None:
            return False
        return self.root_note == other.root_note and \
               self.components_degree_list == other.components_degree_list and \
               self.bass_degree == other.bass_degree

    def __hash__(self):
        return hash((self.root_note, self.bass_degree, self.components_degree_list))

    def __str__(self):
        components = []
        for component in self.components_degree_list:
            components.append(str(component))
        chord_string = mir_eval.chord.join(str(self.root_note), '', components, str(self.bass_degree))
        return chord_string

        # result = [str(self.root_note)]
        # result.append('(')
        # for component in self.components_degree_list:
        #     result.append(str(component))
        # result.append(')')
        # result.append('/')
        # result.append(str(self.bass_degree))
        # return ''.join(result)

    @staticmethod
    def _component_list_from_common_tab_shorthand(shorthand_string):
        shorthands = ['7sus4', '7sus', 'sus2', 'sus4', 'sus', 'm6', '6/9', '6', '7-5', '7\+5', '5', 'm9', 'maj9',
                      'add9', '9', '11', '13', 'maj7', 'M7', 'maj', 'min7', 'm7', 'm', 'dim', 'aug', '+', '7']
        component_lists = [['4', '4', 'b7'], ['4', '4', 'b7'], ['2', '5'], ['4', '5'], ['4', '5'],
                           ['b3', '5', '6'], ['2', '3', '5', '6'], ['3', '5', '6'], ['3', 'b5', 'b7'],
                           ['3', '#5', 'b7'], ['5'], ['2', 'b3', '5', 'b7'], ['2', '3', '5', '7'],
                           ['2', '3', '5'], ['2', '3', '5', 'b7'], ['2', '3', '4', '5', 'b7'],
                           ['2', '3', '4', '5', '6', 'b7'], ['3', '5', '7'], ['3', '5', '7'], ['3', '5'],
                           ['b3', '5', 'b7'], ['b3', '5', 'b7'], ['b3', '5'], ['b3', 'b5'], ['3', '#5'],
                           ['3', '#5'], ['b3', '5', 'b7']]
        if shorthand_string not in shorthands:
            return []
        return component_lists[shorthands.index(shorthand_string)]

    @staticmethod
    def _component_list_from_harte_shorthand(shorthand_string):
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
        # First find non-chord strings
        if chord_string == 'N':
            return None

        # Extract root, shorthand, degree_list and bass_degree from the chord string
        match_chord_string = re.search(
            r'(?P<root>[ABCDEFG][b#]{0,2}):?'
            r'(?P<shorthand>minmaj7|hdim7|maj7|min7|dim7|maj6|min6|maj9|min9|sus9|7|9|maj|min|dim|aug)?'
            r'(\((?P<degree_list>\*?[#b]{0,2}[0-9]{1,2}(,\*?[#b]{0,2}[0-9]{1,2})*)\))?'
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
            bass_degree = Interval(1)
        else:
            bass_degree = Interval.from_harte_interval(match_chord_string.group('bass_degree'))

        # Return the chord
        return cls.from_shorthand_degree_bass(root_note_pitch_class, shorthand_str, degree_str_list, bass_degree)

    @classmethod
    def from_common_tab_notation_string(cls, chord_string):
        chord_parts = re.search(
            r'(?P<root_str>[ABCDEFG][b#]?)'
            r'(?P<chord_type_str>7sus4|7sus|sus2|sus4|sus|m6|6/9|6|7-5|7\+5|5|m9|maj9|add9|9|11|13|maj7|M7|maj|min7|m7'
            r'|m|dim|aug|\+|7)?'
            r'(/(?P<bass_note_str>[ABCDEFG][b#])?)?',
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
            bass_interval = Interval(1)
        else:
            bass_note_pitch_class = PitchClass.from_harte_pitch_class(bass_note_string)
            bass_interval = Interval.from_pitch_class_distances(root_note_pitch_class, bass_note_pitch_class)

        return Chord.from_shorthand_degree_bass(root_note_pitch_class, chord_type_string, [], bass_interval, 'tab')


# c = Chord.from_major('D#')
# c1 = Chord.from_harte_chord_string("C:(3,5)")
# c2 = Chord.from_harte_chord_string("C:(b3,5)")
# c3 = Chord.from_harte_chord_string("D#:(b3,5,b7,9)/5")
# c4 = Chord.from_harte_chord_string("C:min7")
# c5 = Chord.from_harte_chord_string("C:(b3,5,b7)")
# t1 = (c4 == c5)
# c6 = Chord.from_harte_chord_string("C:min7(*5,11)")
# c7 = Chord.from_harte_chord_string("C:(b3,b7,11)")
# t2 = (c6 == c7)
# c8 = Chord.from_harte_chord_string("C")
# c9 = Chord.from_harte_chord_string("C:maj")
# c10 = Chord.from_harte_chord_string("C:(3,5)")
# t3 = (c8 == c9) and (c9 == c10)
# c11 = Chord.from_harte_chord_string("A/3")
# c12 = Chord.from_harte_chord_string("A:maj/3")
# c13 = Chord.from_harte_chord_string("A:(3,5)/3")
# t4 = (c11 == c12) and (c12 == c13)
# c14 = Chord.from_harte_chord_string("C:maj(4)")
# c15 = Chord.from_harte_chord_string("C:(3,4,5)")
# t5 = (c14 == c15)
# t6 = (Chord.from_harte_chord_string("C#") == Chord.from_harte_chord_string("Db"))

# p = Pitch(78)
# p.transpose_by(Interval.from_harte_interval('b3'))
# ui = 3
