import numpy as np
from decibel.utils import filehandler
from decibel.utils.musicobjects import PITCH_CLASSES
from decibel.music_objects.chord import Chord
from decibel.music_objects.interval import Interval


class HMMParameters:
    def __init__(self, train_songs: dict, chords_list: list):
        """
        Train the parameters of the HMM on the training songs

        :param train_songs: Songs on which we train our HMM
        :param chords_list: All possible chords on which we could classify
        """
        # Find alphabet
        self.alphabet = self._chords_list_to_alphabet(chords_list)

        # Initialize chord_beat_matrix_per_chord: a list with |alphabet| x |beats| list for each chord
        chroma_beat_matrix_per_chord = [[] for _ in self.alphabet]

        # Initialize transition_matrix and init_matrix
        self.trans = np.ones((len(self.alphabet), len(self.alphabet)))
        self.init = np.ones(len(self.alphabet))

        # Iterate over the songs; fill chroma_beat_matrix_per_chord, init_matrix and transition_matrix
        for train_song_key in train_songs:
            train_song = train_songs[train_song_key]
            train_song.audio_features_path = filehandler.get_full_audio_features_path(train_song_key)
            if train_song.audio_features_path != '':
                # We have audio features and labels for this song; load them (otherwise ignore the song)
                features = np.load(train_song.audio_features_path)
                chord_index_list = []
                # Iterate over the beats, fill chroma_beat_matrix_per_chord and chord_index_list
                for frame_index in range(features.shape[0]):
                    chroma = features[frame_index, 1:13].astype(float)
                    chord_index = self._get_index_in_alphabet(Chord.from_harte_chord_string(
                        features[frame_index, 13]))
                    chord_index_list.append(chord_index)
                    chroma_beat_matrix_per_chord[chord_index].append(chroma)
                # Add first chord to init_matrix
                self.init[chord_index_list[0]] += 1
                # Add each chord transition to transition_matrix
                for i in range(0, len(chord_index_list) - 1):
                    self.trans[chord_index_list[i], chord_index_list[i + 1]] += 1

        # Normalize transition and init matrices
        self.init = self.init / sum(self.init)
        self.trans = np.array([self.trans[i] / sum(self.trans[i]) for i in range(len(self.alphabet))])

        # Calculate mean and covariance matrices
        self.obs_mu = np.zeros((len(self.alphabet), 12))
        self.obs_sigma = np.zeros((len(self.alphabet), 12, 12))
        for i in range(len(self.alphabet)):
            chroma_beat_matrix_per_chord[i] = np.array(chroma_beat_matrix_per_chord[i]).T
            self.obs_mu[i] = np.mean(chroma_beat_matrix_per_chord[i], axis=1)
            self.obs_sigma[i] = np.cov(chroma_beat_matrix_per_chord[i], ddof=0)

        # Calculate additional values so we can calculate the emission probability more easily
        self.twelve_log_two_pi = 12 * np.log(2 * np.pi)
        self.log_det_sigma = np.zeros(len(self.alphabet))
        self.sigma_inverse = np.zeros(self.obs_sigma.shape)
        for i in range(len(self.alphabet)):
            self.log_det_sigma[i] = np.log(np.linalg.det(self.obs_sigma[i]))
            self.sigma_inverse[i] = np.mat(np.linalg.pinv(self.obs_sigma[i]))

    @staticmethod
    def _chords_list_to_alphabet(chords_list: list) -> list:
        """
        Convert a chords list (key-mode-chroma tuples) to an alphabet (strings that represent the chord)

        :param chords_list: Chord list: [(key-mode-chroma)]
        :return: Alphabet: [chord_str]

        >>> HMMParameters._chords_list_to_alphabet([[1, '', [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]]])
        ['N', 'C#']
        """
        alphabet = ['N']
        for chord_template in chords_list:
            key_nr, mode_str, _ = chord_template
            key_str = PITCH_CLASSES[key_nr]
            alphabet.append(key_str + mode_str)
        return alphabet

    def _get_index_in_alphabet(self, chord: Chord) -> int:
        """
        Find the index of the most similar chord to this chord in the alphabet

        :param chord: Chord for which we want to find the index
        :return: Index of most similar chord in the alphabet
        """
        if len(self.alphabet) == 25:
            # Majmin alphabet
            if chord is None:
                chord_str = 'N'
            elif Interval(3) in chord.components_degree_list:
                chord_str = str(chord.root_note) + 'm'
            else:
                chord_str = str(chord.root_note)
            return self.alphabet.index(chord_str)
        else:
            return 0  # TODO: Implement for other alphabets

    def _read_tab_file_path(self, chords_from_tab_file_path: str) -> (int, np.array, np.array, np.array):
        """
        Load chord information from chords_from_tab_file_path

        :param chords_from_tab_file_path: File that contains chord information
        :return: (nr_of_chords_in_tab, chord_ids, is_first_in_line, is_last_in_line)
        """
        # Load .npy file consisting of: [line_nr, segment_nr, system_nr, chord_x, chord_str]
        chords_from_tab = np.load(chords_from_tab_file_path)
        nr_of_chords_in_tab = chords_from_tab.shape[0]
        # If we found less than 5 chords, we will not use this tab
        if nr_of_chords_in_tab < 5:
            return nr_of_chords_in_tab, [], [], []

        # Chord id's
        line_nrs = chords_from_tab[:, 0].astype(int)
        chord_ids = np.zeros(nr_of_chords_in_tab).astype(int)
        for i in range(nr_of_chords_in_tab):
            chord_ids[i] = self._get_index_in_alphabet(Chord.from_harte_chord_string(chords_from_tab[i, 4]))

        # Array: is this chord first and/or last in its line?
        is_first_in_line = np.zeros(nr_of_chords_in_tab).astype(int)
        is_first_in_line[0] = 1
        for i in range(1, nr_of_chords_in_tab):
            if line_nrs[i] != line_nrs[i - 1]:
                is_first_in_line[i] = 1
        is_last_in_line = np.zeros(nr_of_chords_in_tab).astype(int)
        is_last_in_line[-1] = 1
        for i in range(nr_of_chords_in_tab - 1):
            if line_nrs[i] != line_nrs[i + 1]:
                is_last_in_line[i] = 1

        return nr_of_chords_in_tab, chord_ids, is_first_in_line, is_last_in_line

    def _calculate_altered_transition_matrix(self, nr_of_chords_in_tab: int, chord_ids: np.array,
                                             is_first_in_line: np.array, is_last_in_line: np.array,
                                             p_f: float, p_b: float):
        """
        Calculate an altered transition matrix for the jump alignment algorithm

        :param nr_of_chords_in_tab: Number of chords in the tab file
        :param chord_ids: Numbers of the chords (indexes in the alphabet)
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

        :param chord_label: Chord index in the alphabet (integer)
        :return: Chord string (str)
        """
        if chord_label == 0:
            return 'N'
        return str(Chord.from_common_tab_notation_string(self.alphabet[chord_label]))

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
        if len(self.alphabet) == 25:
            mode = int((chord_label - 1) / 12)
            key = (chord_label - 1) % 12
            key += nr_semitones_higher
            if key >= 12:
                key -= 12
            return 12 * mode + key + 1

        # TODO: implement for other alphabets
        return 0

    def jump_alignment(self, chords_from_tab_file_path: str, audio_features_path: str, lab_write_path: str,
                       p_f: float = 0.05, p_b: float = 0.05) -> (float, int):
        """
        Calculate the optimal alignment between tab file and audio

        :param chords_from_tab_file_path: Path to chords from tab file
        :param audio_features_path: Path to audio features
        :param lab_write_path: Path to the file to write the chord labels to
        :param p_f: Forward probability
        :param p_b: Backward probability
        :return: best likelihood and best transposition
        """
        # Load chord information from chords_from_tab_file_path
        nr_of_chords_in_tab, chord_ids, is_first_in_line, is_last_in_line = \
            self._read_tab_file_path(chords_from_tab_file_path)

        if nr_of_chords_in_tab < 5:
            return None, 0

        # Calculate the emission probability matrix for this song
        features = np.load(audio_features_path)[:, 1:13].astype(float)
        nr_beats = features.shape[0]
        log_emission_probability_matrix = np.zeros((len(self.alphabet), nr_beats))
        for i in range(len(self.alphabet)):
            for b in range(nr_beats):
                om = np.mat(features[b] - self.obs_mu[i])
                log_emission_probability_matrix[i, b] = \
                    (self.log_det_sigma[i] + om * self.sigma_inverse[i] * om.T + self.twelve_log_two_pi) / -2

        best_transposition, best_g, best_tr, best_last_chord, best_likelihood = -1, None, None, -1, -float('inf')

        for semitone_transposition in range(12):
            # Transpose
            transposed_chord_ids = \
                np.array([self._transpose_chord_label(c_i, semitone_transposition) for c_i in chord_ids])

            # Fill altered transition matrix
            altered_transition_matrix = self._calculate_altered_transition_matrix(nr_of_chords_in_tab,
                                                                                  transposed_chord_ids,
                                                                                  is_first_in_line, is_last_in_line,
                                                                                  p_f, p_b)

            # Initialize travel grid
            g = np.zeros((nr_beats, nr_of_chords_in_tab))
            tr = np.zeros((nr_beats, nr_of_chords_in_tab), dtype='uint8')
            for j in range(nr_of_chords_in_tab):
                g[0, j] = log_emission_probability_matrix[transposed_chord_ids[j], 0] + \
                          np.log(self.init[transposed_chord_ids[j]])
            for i in range(1, nr_beats):
                for j in range(nr_of_chords_in_tab):
                    maximum = -float('inf')
                    max_chord = -1
                    for c in range(nr_of_chords_in_tab):
                        if altered_transition_matrix[c, j] > 0 and g[i - 1, c] + \
                                np.log(altered_transition_matrix[c, j]) > maximum:
                            maximum = g[i - 1, c] + np.log(altered_transition_matrix[c, j])
                            max_chord = c
                    g[i, j] = log_emission_probability_matrix[transposed_chord_ids[j], i] + maximum
                    tr[i, j] = max_chord

            # Find log likelihood and best last chord
            log_likelihood = -float('inf')
            last_chord = -1
            for c in range(nr_of_chords_in_tab):
                if g[-1, c] > log_likelihood:
                    log_likelihood = g[-1, c]
                    last_chord = c

            # Save these travel grids only if the transposition had the best likelihood until now
            if log_likelihood > best_likelihood:
                best_transposition, best_g, best_tr, best_last_chord, best_likelihood = \
                    semitone_transposition, g, tr, last_chord, log_likelihood

        # Transpose to the best transposition
        transposed_chord_ids = np.array([self._transpose_chord_label(c_i, best_transposition) for c_i in chord_ids])

        # Derive the Viterbi path
        viterbi_path_reversed = [best_last_chord]
        last_added = best_last_chord
        for b in range(nr_beats - 1, 0, -1):
            viterbi_path_reversed.append(best_tr[b, last_added])
            last_added = best_tr[b, last_added]
        viterbi_path = list(reversed(viterbi_path_reversed))
        viterbi_path = transposed_chord_ids[viterbi_path]

        # Export the Viterbi path
        beat_times = np.load(audio_features_path)[:, 0]
        beat_start = '0'
        last_chord = viterbi_path[0]
        with open(lab_write_path, 'w') as write_file:
            for b in range(len(beat_times) - 2):
                if viterbi_path[b] != last_chord:
                    chord_str = self._chord_label_to_chord_str(viterbi_path[b - 1])
                    write_file.write(beat_start + ' ' + beat_times[b] + ' ' + chord_str + '\n')
                    beat_start = beat_times[b]
                    last_chord = viterbi_path[b]
            if beat_times[len(beat_times) - 2] != beat_start:
                chord_str = self._chord_label_to_chord_str(viterbi_path[len(beat_times) - 2])
                write_file.write(beat_start + ' ' + beat_times[len(beat_times) - 1] + ' ' + chord_str)

        return best_likelihood, best_transposition


def train(chords_list, training_set) -> HMMParameters:
    """
    Train the HMM parameters on training_set for the given chords_list vocabulary

    :param chords_list: List of chords in our vocabulary
    :param training_set: Set of songs for training
    :return: HMM Parameters
    """
    return HMMParameters(training_set, chords_list)


def test_single_song(song, hmm_parameters) -> None:
    """
    Estimate chords for each tab matched to the song and export them to a lab file.

    :param song: Song for which we estimate tab-based chords
    :param hmm_parameters: Parameters of the trained HMM
    """
    if song.audio_features_path != '':
        # There are audio features for this path
        for full_tab_path in song.full_tab_paths:
            tab_chord_path = filehandler.get_chords_from_tab_filename(full_tab_path)
            tab_write_path = filehandler.get_full_tab_chord_labs_path(full_tab_path)
            if not filehandler.file_exists(tab_write_path):
                log_likelihood, transposition_semitone = \
                    hmm_parameters.jump_alignment(tab_chord_path, song.audio_features_path,
                                                  tab_write_path)
                if log_likelihood is not None:
                    # We found an alignment, write this to our log-likelihoods file
                    if not tab_write_path.startswith(filehandler.DATA_PATH):
                        print('WRITING ERROR')
                    # Remove start of path
                    tab_write_path = tab_write_path[len(filehandler.DATA_PATH) + 1:]
                    filehandler.write_log_likelihood(song.key, tab_write_path, log_likelihood, transposition_semitone)
