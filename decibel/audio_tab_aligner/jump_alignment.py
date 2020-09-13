import numpy as np

from decibel.audio_tab_aligner.hmm_parameters import HMMParameters
from decibel.import_export import filehandler
from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song


def _read_tab_file_path(chords_from_tab_file_path: str) -> (int, np.array, np.array, np.array):
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
        chord_ids[i] = self.alphabet.get_index_of_chord_in_alphabet(
            Chord.from_harte_chord_string(chords_from_tab[i, 4]))

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


def train(chords_list: ChordVocabulary, training_set) -> HMMParameters:
    """
    Train the HMM parameters on training_set for the given chords_list vocabulary

    :param chords_list: List of chords in our vocabulary
    :param training_set: Set of songs for training
    :return: HMM Parameters
    """
    return HMMParameters(training_set, chords_list)


def jump_alignment(chords_from_tab_file_path: str, audio_features_path: str, lab_write_path: str,
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
    alphabet_size = len(self.alphabet.alphabet_list)
    features = np.load(audio_features_path)[:, 1:13].astype(float)
    nr_beats = features.shape[0]
    log_emission_probability_matrix = np.zeros((alphabet_size, nr_beats))
    for i in range(alphabet_size):
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


def test_single_song(song: Song, hmm_parameters: HMMParameters) -> None:
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
