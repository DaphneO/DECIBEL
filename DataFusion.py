from math import ceil
import numpy as np
import Chords
import FileHandler
import random


def load_lab_file_into_chord_matrix(lab_path, i, chord_matrix, alphabet, nr_of_samples):
    with open(lab_path, 'r') as read_file:
        chord_annotation = read_file.readlines()
        chord_annotation = [x.rstrip().split() for x in chord_annotation]
        res = []
        for y in chord_annotation:
            start_time, end_time = float(y[0]), float(y[1])
            chord_label_alphabet_index = get_index_in_alphabet(Chords.Chord.from_harte_chord_string(y[2]), alphabet)
            res.append([start_time, end_time, chord_label_alphabet_index])
            for s in range(int(start_time * 100), min(int(end_time * 100), nr_of_samples - 1)):
                chord_matrix[i, s] = chord_label_alphabet_index


def chords_list_to_alphabet(chords_list):
    alphabet = ['N']
    for chord_template in chords_list:
        key_nr, mode_str, _ = chord_template
        key_str = Chords.PITCH_CLASSES[key_nr]
        alphabet.append(key_str + mode_str)
    return alphabet


def get_index_in_alphabet(chord, alphabet):
    if len(alphabet) == 25:
        # Majmin alphabet
        if chord is None:
            chord_str = 'N'
        elif Chords.Interval(3) in chord.components_degree_list:
            chord_str = str(chord.root_note) + 'm'
        else:
            chord_str = str(chord.root_note)
        if chord_str not in alphabet:
            foutje = True
        return alphabet.index(chord_str)
    else:
        return 0  # TODO Nog implementeren voor andere alphabets


def _write_final_labels(final_labels, lab_path, alphabet):
    write_labels = []
    start_time = -1
    last_chord = ''
    last_added = True
    for i in range(len(final_labels)):
        if final_labels[i] == last_chord:
            last_added = False
        else:
            if not last_added:
                # Write previous chord
                write_labels.append((start_time, float(i) / 100, last_chord))
            # Set parameters for next
            start_time = float(i) / 100
            last_chord = final_labels[i]
    if not last_added:
        # Write last chord
        write_labels.append((start_time, float(len(final_labels) - 1) / 100, last_chord))

    with open(lab_path, 'w') as write_file:
        for write_label in write_labels:
            chord_string = str(Chords.Chord.from_common_tab_notation_string(alphabet[write_label[2]]))
            if chord_string == 'None':
                chord_string = 'N'
            write_file.write('{0} {1} {2}\n'.format(str(write_label[0]), str(write_label[1]), chord_string))


# def _get_labs(song, all_or_expected_best, with_chordify=True):
#     if all_or_expected_best == 'all':
#         # Use the results of all MIDIs and tabs
#         return [result[2] for result in song.results]
#
#     # Keep only the expected best MIDIs and tabs. Remove MIDIs with alignment error of more than 0.85
#     expected_best_labs = []
#     best_midi = '', 0
#     best_tab = '', 0
#     for result in song.results:
#         if result[0] == 'chordify':
#             if with_chordify:
#                 expected_best_labs.append(result[2])
#         elif result[0][:4] == 'midi':
#             if result[7] <= 0.85 and result[8] > best_midi[1]:
#                 best_midi = result[2], result[8]
#         elif result[0] == 'tab':
#             if result[8] > best_tab[1]:
#                 best_tab = result[2], result[8]
#     if best_midi[0] != '':
#         expected_best_labs.append(best_midi[0])
#     if best_tab[0] != '':
#         expected_best_labs.append(best_tab[0])
#     return expected_best_labs


def get_labs(song):
    all_labs, expected_best_labs, audio_labs = [], [], []
    best_midi_lab, best_midi_quality = '', 0
    best_tab_lab, best_tab_quality = '', 0
    for result in song.results:
        if result[0] == 'chordify':
            # This is a result from an audio ACE system, so add to the audio labs
            audio_labs.append((result[2], 'CHF'))
        elif result[0][:4] == 'midi':
            # This is a result from the MIDI ACE system
            if result[7] <= 0.85:
                # The MIDI is well aligned, so we will use it
                all_labs.append(result[2])
                if result[8] > best_midi_quality:
                    # This is the best MIDI for this song so far
                    best_midi_lab, best_midi_quality = result[2], result[8]
        elif result[0] == 'tab':
            # This is a result from the Tab ACE system, so we will use it
            all_labs.append(result[2])
            if result[8] > best_tab_quality:
                best_tab_lab, best_tab_quality = result[2], result[8]
    if best_midi_lab != '':
        expected_best_labs.append(best_midi_lab)
    if best_tab_lab != '':
        expected_best_labs.append(best_tab_lab)
    for mirex_submission_name in FileHandler.MIREX2017_SUBMISSION_NAMES:
        audio_labs.append((song.full_mirex_2017_chord_lab_paths[mirex_submission_name], mirex_submission_name))
    return all_labs, expected_best_labs, audio_labs


def _random_chord_label_combination(chord_matrix, nr_of_samples):
    final_labels = np.empty(nr_of_samples, dtype=int)
    for sample_nr in range(nr_of_samples):
        # Select at every sample the chord from a random source
        source_nr = random.randint(0, chord_matrix.shape[0] - 1)
        final_labels[sample_nr] = chord_matrix[source_nr, sample_nr]
    return final_labels


def _majority_vote_chord_label_combination(chord_matrix, nr_of_samples, alphabet):
    final_labels = np.empty(nr_of_samples, dtype=int)
    for sample_nr in range(nr_of_samples):
        # Select at every sample the most frequent chord (or a random one of multiple most frequent chords)
        frequencies = np.zeros(len(alphabet))
        for lab_nr in range(chord_matrix.shape[0]):
            frequencies[chord_matrix[lab_nr, sample_nr]] += 1
        most_occuring_chord_indices = np.argwhere(frequencies == np.amax(frequencies))
        chosen_chord_index = most_occuring_chord_indices[random.randint(0, len(most_occuring_chord_indices) - 1)]
        final_labels[sample_nr] = chosen_chord_index
    return final_labels


def _data_fusion_chord_label_combination(chord_matrix, nr_of_samples, alphabet):
    # Calculate initial chord label probabilities
    chord_label_probabilities = np.empty((nr_of_samples, len(alphabet)))
    for sample_nr in range(nr_of_samples):
        for chord_nr in range(len(alphabet)):
            chord_label_probabilities[sample_nr, chord_nr] = \
                np.mean([chord_matrix[lab_nr, sample_nr] == chord_nr for lab_nr in range(chord_matrix.shape[0])])

    # Calculate source accuracies
    for i in range(5):
        source_accuracies = np.empty(chord_matrix.shape[0])
        for lab_nr in range(chord_matrix.shape[0]):
            source_accuracies[lab_nr] = np.mean(
                [chord_label_probabilities[sample_nr, chord_matrix[lab_nr, sample_nr]]
                 for sample_nr in range(nr_of_samples)])

        chord_label_probabilities = np.empty((nr_of_samples, len(alphabet)))
        for sample_nr in range(nr_of_samples):
            vote_counts = np.zeros(len(alphabet))
            for lab_nr in range(chord_matrix.shape[0]):
                vote_counts[chord_matrix[lab_nr, sample_nr]] += source_accuracies[lab_nr]
            sum_exp_vote_counts_all_labels = sum([np.exp(vote_counts[chord_nr]) for chord_nr in range(len(alphabet))])
            for chord_nr in range(len(alphabet)):
                chord_label_probabilities[sample_nr, chord_nr] = \
                    np.exp(vote_counts[chord_nr]) / sum_exp_vote_counts_all_labels

    final_labels = np.empty(nr_of_samples, dtype=int)
    for sample_nr in range(nr_of_samples):
        final_labels[sample_nr] = np.argmax(chord_label_probabilities[sample_nr])

    return final_labels


def data_fuse_song(song, chords_list):
    # Specify the .lab files we are going to fuse
    all_labs, expected_best_labs, audio_labs = get_labs(song)

    # Sample every 10ms, so 100 samples per second
    song_duration = song.duration
    nr_of_samples = int(ceil(song_duration * 100))

    # Turn the chords list (a list of (key, mode-str, chroma-list) tuples) into an alphabet (a list of strings)
    alphabet = chords_list_to_alphabet(chords_list)

    # Iterate over the two types of selection (all / best)
    for lab_list_i in [0, 1]:
        lab_list = [all_labs, expected_best_labs][lab_list_i]
        selection_name = ['all', 'best'][lab_list_i]

        # Fill a numpy array with chord labels for each of the lab files
        chord_matrix = np.zeros((len(lab_list) + 1, nr_of_samples), dtype=int)
        for lab_nr in range(len(lab_list)):
            load_lab_file_into_chord_matrix(lab_list[lab_nr], lab_nr, chord_matrix, alphabet, nr_of_samples)

        # Iterate over the seven audio types:
        for (audio_lab, audio_name) in audio_labs:
            if FileHandler.file_exists(audio_lab):
                # Add the lab file to our chord matrix
                load_lab_file_into_chord_matrix(audio_lab, len(lab_list), chord_matrix, alphabet, nr_of_samples)
                # Iterate over the three combination types; calculate labels and write them:
                final_labels_random = _random_chord_label_combination(chord_matrix, nr_of_samples)
                final_labels_majority = _majority_vote_chord_label_combination(chord_matrix, nr_of_samples, alphabet)
                final_labels_data_fusion = _data_fusion_chord_label_combination(chord_matrix, nr_of_samples, alphabet)
                _write_final_labels(final_labels_random,
                                    FileHandler.get_data_fusion_path(song.key, 'rand', selection_name, audio_name),
                                    alphabet)
                _write_final_labels(final_labels_majority,
                                    FileHandler.get_data_fusion_path(song.key, 'mv', selection_name, audio_name),
                                    alphabet)
                _write_final_labels(final_labels_data_fusion,
                                    FileHandler.get_data_fusion_path(song.key, 'df', selection_name, audio_name),
                                    alphabet)
    i = 0


# def data_fuse_song_old(song, chords_list):
#     # Specify the paths to the .lab files we are going to fuse
#     all_labs = _get_labs(song, 'all')
#     expected_best_labs = _get_labs(song, 'expected best')
#
#     # Sample every 10ms, so 100 samples per second
#     song_duration = song.duration
#     nr_of_samples = int(ceil(song_duration * 100))
#
#     # Turn the chords list (a list of (key, mode-str, chroma-list) tuples) into an alphabet (a list of strings)
#     alphabet = chords_list_to_alphabet(chords_list)
#
#     # Fill a numpy array with chord labels for each of the lab files
#     chord_matrix_all = np.zeros((len(all_labs), nr_of_samples), dtype=int)
#     for lab_nr in range(len(all_labs)):
#         load_lab_file_into_chord_matrix(all_labs[lab_nr], lab_nr, chord_matrix_all, alphabet, nr_of_samples)
#     chord_matrix_expected_best = np.zeros((len(expected_best_labs), nr_of_samples), dtype=int)
#     for lab_nr in range(len(expected_best_labs)):
#         load_lab_file_into_chord_matrix(expected_best_labs[lab_nr], lab_nr, chord_matrix_expected_best, alphabet,
#                                         nr_of_samples)
#
#     # 4 ways of data fusion: Random / Majority Vote / Data Fuse All / Data Fuse Expected Best
#     final_labels_random = _random_chord_label_combination(all_labs, chord_matrix_all, nr_of_samples)
#     final_labels_majority = _majority_vote_chord_label_combination(all_labs, chord_matrix_all, nr_of_samples, alphabet)
#     final_labels_df_all = _data_fusion_chord_label_combination(all_labs, chord_matrix_all,
#                                                                nr_of_samples, alphabet, 'all')
#     final_labels_df_best = _data_fusion_chord_label_combination(expected_best_labs, chord_matrix_expected_best,
#                                                                 nr_of_samples, alphabet, 'best')
#
#
#     # Write labels
#     _write_final_labels(final_labels_random, FileHandler.get_data_fusion_path(song.key, 'rand'), alphabet)
#     _write_final_labels(final_labels_majority, FileHandler.get_data_fusion_path(song.key, 'mv'), alphabet)
#     _write_final_labels(final_labels_df_all, FileHandler.get_data_fusion_path(song.key, 'all'), alphabet)
#     _write_final_labels(final_labels_df_best, FileHandler.get_data_fusion_path(song.key, 'best'), alphabet)


# def mirex_data_fuse_song_old(song, chords_list):
#     # Specify the paths to the .lab files we are going to fuse
#     expected_best_labs = _get_labs(song, 'expected best', False)
#
#     # Sample every 10ms, so 100 samples per second
#     song_duration = song.duration
#     nr_of_samples = int(ceil(song_duration * 100))
#
#     # Turn the chords list (a list of (key, mode-str, chroma-list) tuples) into an alphabet (a list of strings)
#     alphabet = chords_list_to_alphabet(chords_list)
#
#     # Fill a numpy array with chord labels for each of the lab files
#     chord_matrix_expected_best = np.zeros((len(expected_best_labs) + 1, nr_of_samples), dtype=int)
#     for lab_nr in range(len(expected_best_labs)):
#         load_lab_file_into_chord_matrix(expected_best_labs[lab_nr], lab_nr, chord_matrix_expected_best,
#                                         alphabet, nr_of_samples)
#
#     for mirex_submission_name in FileHandler.MIREX2017_SUBMISSION_NAMES:
#         lab_name = song.full_mirex_2017_chord_lab_paths[mirex_submission_name]
#         if FileHandler.file_exists(lab_name):
#             expected_best_labs.append(lab_name)
#             load_lab_file_into_chord_matrix(lab_name, len(expected_best_labs) - 1, chord_matrix_expected_best,
#                                             alphabet, nr_of_samples)
#             df_labels = _data_fusion_chord_label_combination(expected_best_labs, chord_matrix_expected_best,
#                                                              nr_of_samples, alphabet)
#             _write_final_labels(df_labels,
#                                 FileHandler.get_mirex_data_fusion_path(song.key, mirex_submission_name), alphabet)
#             expected_best_labs.remove(lab_name)


# def data_fuse_all_songs(all_songs, chords_list):
#     for song_key in all_songs:
#         if not FileHandler.file_exists(FileHandler.get_data_fusion_path(song_key, 'best')):
#             data_fuse_song(all_songs[song_key], chords_list)
#
#
# def data_fuse_all_songs_mirex(all_songs, chords_list):
#     for song_key in all_songs:
#         if not FileHandler.file_exists(FileHandler.get_mirex_data_fusion_path(song_key, 'WL1')):
#             mirex_data_fuse_song(all_songs[song_key], chords_list)
