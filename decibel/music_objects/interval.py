from decibel.utils.find_item_in_list import find_item


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


class Interval:
    def __init__(self, semitone_interval):
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
        """
        Check if two intervals sound the same (although they may be called by different Harte labels)

        :param other: The other interval
        :return: Do two intervals soud the same?

        >>> Interval.from_harte_interval('#4') == Interval.from_harte_interval('b5')
        True
        """
        return self.semitone_interval == other.semitone_interval

    def __hash__(self):
        """
        Get a unique integer that identifies this Interval
        :return: Unique integer that identifies this Interval
        """
        return hash(self.semitone_interval)

    def __lt__(self, other):
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