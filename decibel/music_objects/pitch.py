import math

from decibel.music_objects.pitch_class import PitchClass
from decibel.music_objects.interval import Interval


class Pitch:
    def __init__(self, midi_pitch):
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
    def from_pitch_class_and_octave_number(cls, pitch_class: PitchClass, octave_number):
        """
        Create a Pitch instance based on its pitch class and octave number (e.g. 'A' and 4)

        :param pitch_class: Pitch class string (e.g. 'A')
        :param octave_number: Octave number (e.g. 4)
        :return: Pitch, as specified by the pitch class and octave number

        >>> p = Pitch.from_pitch_class_and_octave_number(PitchClass.from_harte_pitch_class('A'), 4)
        >>> p.midi_pitch
        69
        >>> p.harte_pitch_class
        ['G##', 'A', 'Bbb']
        """
        return cls(12 * octave_number + pitch_class.pitch_class_number + 12)

    @classmethod
    def from_pitch_name(cls, pitch_name):
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
            return cls.from_pitch_class_and_octave_number(
                PitchClass.from_harte_pitch_class(pitch_name[0:2]), int(pitch_name[2:]))
        return cls.from_pitch_class_and_octave_number(
            PitchClass.from_harte_pitch_class(pitch_name[0]), int(pitch_name[1:]))

    def _midi_pitch_to_pitch_class(self):
        """
        Get the pitch class from the midi pitch of our Pitch object

        :return: Pitch class from the midi pitch of our Pitch object

        >>> str(Pitch(69)._midi_pitch_to_pitch_class())
        'A'
        """
        return PitchClass(self.midi_pitch % 12)

    def _midi_pitch_to_harte_class(self):
        """
        Get the harte class from the midi pitch of our Pitch object

        :return: Harte class from the midi pitch of our Pitch object

        >>> Pitch(69)._midi_pitch_to_harte_class()
        ['G##', 'A', 'Bbb']
        """
        return PitchClass(self.midi_pitch % 12).harte_pitch_class

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
