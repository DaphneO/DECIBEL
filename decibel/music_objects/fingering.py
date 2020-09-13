from decibel.music_objects.pitch import Pitch


class Fingering:
    def __init__(self, base_fret, e2, a2, d3, g3, b3, e4):
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
        >>> str_pitch_classes = [str(pitch_class) for pitch_class in list(f.pitch_class_set)]
        >>> str_pitch_classes.sort()
        >>> str_pitch_classes
        ['A', 'C', 'E']
        >>> str(f.bass_pitch.pitch_class)
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
        """
        Convert the Fingering to a unique integer value, so we can use it as key in a dictionary

        :return: A unique integer value for this Fingering
        """
        return hash((self.base_fret, self.finger_list))

    def __eq__(self, other):
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
            result[pitch_class.pitch_class_number] = 1
        result.append(self.bass_pitch.midi_pitch % 12)
        return result
