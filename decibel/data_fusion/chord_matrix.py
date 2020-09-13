import numpy as np

from decibel.music_objects.chord_alphabet import ChordAlphabet
from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_vocabulary import ChordVocabulary


class ChordMatrix:
    def __init__(self, nr_of_representations: int, nr_of_samples: int, chord_vocabulary: ChordVocabulary):
        self.array = np.zeros((nr_of_representations, nr_of_samples), dtype=int)
        self._first_empty_row = 0
        self._nr_of_representations = nr_of_representations
        self._nr_of_samples = nr_of_samples
        self._chord_alphabet = ChordAlphabet(chord_vocabulary)

    def append_lab_file(self, lab_path: str):
        if self._first_empty_row < self._nr_of_representations:
            self._load_lab_file_into_chord_matrix(lab_path, self._first_empty_row)
            self._first_empty_row += 1
        else:
            raise IndexError('Index out of bounds; the chord matrix seems to be full already.')

    def _load_lab_file_into_chord_matrix(self, lab_path: str, i: int):
        """
        Load a chord file (in Harte's chord annotation format) into a chord matrix.

        :param lab_path: Path to the .lab file with chord annotation/estimation
        :param i: Index to the row in the chord_matrix to fill
        """
        with open(lab_path, 'r') as read_file:
            # Read chord annotation from file
            chord_annotation = read_file.readlines()
            chord_annotation = [x.rstrip().split() for x in chord_annotation]
            for y in chord_annotation:
                # Parse start and end time, retrieve index of chord
                start_time, end_time = float(y[0]), float(y[1])
                chord = Chord.from_harte_chord_string(y[2])
                chord_label_alphabet_index = self._chord_alphabet.get_index_of_chord_in_alphabet(chord)

                # Add chord index to each entry in the chord_matrix that is between start and end time
                for s in range(int(start_time * 100), min(int(end_time * 100), self._nr_of_samples - 1)):
                    self.array[i, s] = chord_label_alphabet_index
