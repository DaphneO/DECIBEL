from decibel.music_objects.chord import Chord


class ChordAnnotationItem:
    def __init__(self, from_time: float, to_time: float, chord: Chord):
        self.from_time = from_time
        self.to_time = to_time
        self.chord = chord
