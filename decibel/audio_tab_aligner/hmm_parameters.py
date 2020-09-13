from typing import Dict

import numpy as np

from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_alphabet import ChordAlphabet
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from decibel.import_export import filehandler


class HMMParameters:
    def __init__(self, train_songs: Dict[int, Song], chord_vocabulary: ChordVocabulary):
        """
        Train the parameters of the HMM on the training songs

        :param train_songs: Songs on which we train our HMM
        :param chord_vocabulary: Vocabulary of all possible chords on which we could classify
        """
        # Convert the vocabulary to a ChordAlphabet
        self.alphabet = ChordAlphabet(chord_vocabulary)
        alphabet_size = len(self.alphabet.alphabet_list)

        # Initialize chord_beat_matrix_per_chord: a list with |chord_vocabulary| x |beats| list for each chord
        chroma_beat_matrix_per_chord = [[] for _ in self.alphabet.alphabet_list]

        # Initialize transition_matrix and init_matrix
        self.trans = np.ones((alphabet_size, alphabet_size))
        self.init = np.ones(alphabet_size)

        # Iterate over the songs; fill chroma_beat_matrix_per_chord, init_matrix and transition_matrix
        for train_song_key, train_song in train_songs.items():
            train_song.audio_features_path = filehandler.get_full_audio_features_path(train_song_key)
            if train_song.audio_features_path != '':
                # We have audio features and labels for this song; load them (otherwise ignore the song)
                features = np.load(train_song.audio_features_path)
                chord_index_list = []
                # Iterate over the beats, fill chroma_beat_matrix_per_chord and chord_index_list
                for frame_index in range(features.shape[0]):
                    chroma = features[frame_index, 1:13].astype(float)
                    chord_index = self.alphabet.get_index_of_chord_in_alphabet(
                        Chord.from_harte_chord_string(features[frame_index, 13]))
                    chord_index_list.append(chord_index)
                    chroma_beat_matrix_per_chord[chord_index].append(chroma)
                # Add first chord to init_matrix
                self.init[chord_index_list[0]] += 1
                # Add each chord transition to transition_matrix
                for i in range(0, len(chord_index_list) - 1):
                    self.trans[chord_index_list[i], chord_index_list[i + 1]] += 1

        # Normalize transition and init matrices
        self.init = self.init / sum(self.init)
        self.trans = np.array([self.trans[i] / sum(self.trans[i]) for i in range(alphabet_size)])

        # Calculate mean and covariance matrices
        self.obs_mu = np.zeros((alphabet_size, 12))
        self.obs_sigma = np.zeros((alphabet_size, 12, 12))
        for i in range(alphabet_size):
            chroma_beat_matrix_per_chord[i] = np.array(chroma_beat_matrix_per_chord[i]).T
            self.obs_mu[i] = np.mean(chroma_beat_matrix_per_chord[i], axis=1)
            self.obs_sigma[i] = np.cov(chroma_beat_matrix_per_chord[i], ddof=0)

        # Calculate additional values so we can calculate the emission probability more easily
        self.twelve_log_two_pi = 12 * np.log(2 * np.pi)
        self.log_det_sigma = np.zeros(alphabet_size)
        self.sigma_inverse = np.zeros(self.obs_sigma.shape)
        for i in range(alphabet_size):
            self.log_det_sigma[i] = np.log(np.linalg.det(self.obs_sigma[i]))
            self.sigma_inverse[i] = np.mat(np.linalg.pinv(self.obs_sigma[i]))

    def _calculate_altered_transition_matrix(self, nr_of_chords_in_tab: int, chord_ids: np.array,
                                             is_first_in_line: np.array, is_last_in_line: np.array,
                                             p_f: float, p_b: float):
        """
        Calculate an altered transition matrix for the jump alignment algorithm

        :param nr_of_chords_in_tab: Number of chords in the tab file
        :param chord_ids: Numbers of the chords (indexes in the chord_vocabulary)
        :param is_first_in_line: Boolean array: is this chord first in its line?
        :param is_last_in_line: Boolean array: is this chord last in its line?
        :param p_f: Forward probability
        :param p_b: Backward probability
        :return: New transition matrix
        """
        altered_transition_matrix = np.zeros((nr_of_chords_in_tab, nr_of_chords_in_tab))
        for i in range(nr_of_chords_in_tab):
            for j in range(nr_of_chords_in_tab):
                if i == j:
                    altered_transition_matrix[i, j] = self.trans[chord_ids[i], chord_ids[i]]
                elif i == j - 1:
                    altered_transition_matrix[i, j] = self.trans[chord_ids[i], chord_ids[j]]
                elif is_last_in_line[i] == 1 and is_first_in_line[j] == 1:
                    if i < j:
                        altered_transition_matrix[i, j] = p_f * self.trans[chord_ids[i], chord_ids[j]]
                    else:
                        altered_transition_matrix[i, j] = p_b * self.trans[chord_ids[i], chord_ids[j]]
        # Normalize altered transition matrix
        for i in range(nr_of_chords_in_tab):
            altered_transition_matrix[i] = altered_transition_matrix[i] / sum(altered_transition_matrix[i])

        return altered_transition_matrix

    def _chord_label_to_chord_str(self, chord_label: int) -> str:
        """
        Translate the integer chord label to a chord string

        :param chord_label: Chord index in the chord_vocabulary (integer)
        :return: Chord string (str)
        """
        if chord_label == 0:
            return 'N'
        return str(Chord.from_common_tab_notation_string(self.alphabet.alphabet_list[chord_label]))

    def _transpose_chord_label(self, chord_label: int, nr_semitones_higher: int) -> int:
        """
        Transpose a chord label up with the specified number of semitones

        :param chord_label: The index of the chord label that needs to be higher
        :param nr_semitones_higher: The number of semitones the chord label needs to be higher
        :return: Index of the transposed chord label
        """
        if chord_label == 0:
            return 0
        nr_semitones_higher = nr_semitones_higher % 12
        if self.alphabet.chord_vocabulary_name == 'MajMin':
            mode = int((chord_label - 1) / 12)
            key = (chord_label - 1) % 12
            key += nr_semitones_higher
            if key >= 12:
                key -= 12
            return 12 * mode + key + 1

        raise NotImplementedError('This is not (yet?) supported for chord vocabularies other than "MajMin".')
        # TODO Implement for other chord vocabularies (e.g. seventh chords)
