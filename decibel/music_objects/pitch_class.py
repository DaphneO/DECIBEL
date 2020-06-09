from decibel.utils.musicobjects import HARTE_PITCH_CLASSES, PITCH_CLASSES, _find_item


class PitchClass:
    def __init__(self, pitch_class_number):
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
        """
        Hashes a PitchClass to an int, so we can use it as dictionary index
        :return: Hashed PitchClass
        """
        return hash(self.pitch_class_number)

    def __str__(self):
        """
        Gets an easily readable name for the pitch Class (instead of a list of Harte pitch classes)

        :return: Easily readable name for the pitch Class

        >>> str(PitchClass(1))
        'C#'
        """
        return PITCH_CLASSES[self.pitch_class_number]

    @classmethod
    def from_harte_pitch_class(cls, harte_pitch_class):
        """
        Create a PitchClass object from its Harte pitch class

        :param harte_pitch_class: A string that defines a pitch class with at most two sharps/flats
        :return: PitchClass as specified by the Harte pitch class

        >>> PitchClass.from_harte_pitch_class('Gbb').pitch_class_number
        5
        """
        pitch_class_number = _find_item(HARTE_PITCH_CLASSES, harte_pitch_class)
        return cls(pitch_class_number)