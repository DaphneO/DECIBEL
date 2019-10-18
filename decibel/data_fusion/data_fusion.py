from math import ceil
import numpy as np
from os import path
from decibel.utils.musicobjects import Chord, PITCH_CLASSES, Interval
from decibel.utils import filehandler


def load_lab_file_into_chord_matrix(lab_path, i, chord_matrix, alphabet, nr_of_samples):
    """
    Load a chord file (in Harte's chord annotation format) into a chord matrix, having the chord label per 10ms sample.

    :param lab_path: Path to the .lab file with chord annotation/estimation
    :param i: Index to the row in the chord_matrix to fill
    :param chord_matrix: Chord matrix to which we add samples from this .lab file
    :param alphabet: The chord vocabulary (used to get the index belonging to a chord string)
    :param nr_of_samples: Total number of samples in the song
    :return: Chord matrix to which we just added samples from this .lab file to row i
    """
    with open(lab_path, 'r') as read_file:
        # Read chord annotation from file
        chord_annotation = read_file.readlines()
        chord_annotation = [x.rstrip().split() for x in chord_annotation]
        for y in chord_annotation:
            # Parse start and end time, retrieve index of chord
            start_time, end_time = float(y[0]), float(y[1])
            chord_label_alphabet_index = _get_index_in_alphabet(Chord.from_harte_chord_string(y[2]), alphabet)

            # Add chord index to each entry in the chord_matrix that is between start and end time
            for s in range(int(start_time * 100), min(int(end_time * 100), nr_of_samples - 1)):
                chord_matrix[i, s] = chord_label_alphabet_index


def _chords_list_to_alphabet(chords_list):
    """
    Turn the chords list (a list of (key, mode-str, chroma-list) tuples) into an alphabet (a list of strings)

    :param chords_list: a list of (key, mode-str, chroma-list) tuples
    :return: an alphabet (a list of strings)
    """
    alphabet = ['N']
    for chord_template in chords_list:
        key_nr, mode_str, _ = chord_template
        key_str = PITCH_CLASSES[key_nr]
        alphabet.append(key_str + mode_str)
    return alphabet


def _get_index_in_alphabet(chord, alphabet):
    """
    Given a Chord object, retrieve the index in the alphabet (our chord vocabulary)

    :param chord: Chord object for which we want to find the index
    :param alphabet: Chord vocabulary
    :return: Index of this chord in the vocabulary
    """
    if len(alphabet) == 25:
        # Majmin alphabet
        if chord is None:
            chord_str = 'N'
        elif Interval(3) in chord.components_degree_list:
            chord_str = str(chord.root_note) + 'm'
        else:
            chord_str = str(chord.root_note)
        if chord_str not in alphabet:
            raise KeyError('Chord string not in alphabet')
        return alphabet.index(chord_str)
    else:
        return 0  # TODO Implement for other alphabets (e.g. seventh chords)


def _write_final_labels(final_labels, lab_path, alphabet):
    """
    Write the row of final labels (after data fusion) from the chord matrix to a .lab file at lab_path

    :param final_labels: The row of final labels after data fusion
    :param lab_path: The path to write the final lab file to
    :param alphabet: The chord vocabulary (used to translate chord indices to chord strings)
    """

    # First, we fill the write_labels list with (start_time, end_time, chord_string) 3-tuples
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
        # The last chord has not been added yet, so we do it now
        write_labels.append((start_time, float(len(final_labels) - 1) / 100, last_chord))

    # Now write the chords to the .lab file in Harte format
    with open(lab_path, 'w') as write_file:
        for write_label in write_labels:
            chord_string = str(Chord.from_common_tab_notation_string(alphabet[write_label[2]]))
            if chord_string == 'None':
                chord_string = 'N'
            write_file.write('{0} {1} {2}\n'.format(str(write_label[0]), str(write_label[1]), chord_string))


def _random_chord_label_combination(chord_matrix, nr_of_samples):
    """
    For each 10ms segment, pick the chord label from a random source

    :param chord_matrix: The chord label matrix
    :param nr_of_samples: Total number of 10ms samples
    :return: Array with the final chord index for each segment
    """
    final_labels = np.empty(nr_of_samples, dtype=int)
    for sample_nr in range(nr_of_samples):
        # Select at every sample the chord from a random source
        source_nr = filehandler.random.randint(0, chord_matrix.shape[0] - 1)
        final_labels[sample_nr] = chord_matrix[source_nr, sample_nr]
    return final_labels


def _majority_vote_chord_label_combination(chord_matrix, nr_of_samples, alphabet):
    """
    For each 10ms segment, pick the chord label that occurs in most sources (or randomly pick one of the chord labels
    that occur in most sources)

    :param chord_matrix: The chord label matrix
    :param nr_of_samples: Total number of 10ms samples
    :param alphabet: The chord vocabulary
    :return: Array with the final chord index for each segment
    """
    final_labels = np.empty(nr_of_samples, dtype=int)
    for sample_nr in range(nr_of_samples):
        # Select at every sample the most frequent chord (or a random one of multiple most frequent chords)
        frequencies = np.zeros(len(alphabet))
        for lab_nr in range(chord_matrix.shape[0]):
            frequencies[chord_matrix[lab_nr, sample_nr]] += 1
        most_occurring_chord_indices = np.argwhere(frequencies == np.amax(frequencies))
        chosen_chord_index = most_occurring_chord_indices[
            filehandler.random.randint(0, len(most_occurring_chord_indices) - 1)]
        final_labels[sample_nr] = chosen_chord_index
    return final_labels


def _data_fusion_chord_label_combination(chord_matrix, nr_of_samples, alphabet):
    """
    For each 10ms segment, pick the chord label using data fusion (i.e. based on chord label probabilities and source
    accuracies)

    :param chord_matrix: The chord label matrix
    :param nr_of_samples: Total number of 10ms samples
    :param alphabet: The chord vocabulary
    :return: Array with the final chord index for each segment
    """
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
    """
    Data fuse a song using all combinations of selection and combination methods, write the final labels to .lab files

    :param song: The song on which we want to apply data fusion
    :param chords_list: The chord vocabulary
    """
    # Check if data fusion has already been calculated  TODO: make this check more robust
    if path.isfile(filehandler.get_data_fusion_path(song.key, 'df', 'best', 'CHF_2017')):
        return

    # Get list of symbolic lab files (all / expected best)
    well_aligned_midis = filehandler.get_well_aligned_midis(song)
    all_symbolic_labs = \
        [filehandler.get_full_midi_chord_labs_path(wam, 'bar') for wam in well_aligned_midis] + \
        [filehandler.get_full_midi_chord_labs_path(wam, 'beat') for wam in well_aligned_midis] + \
        [filehandler.get_full_tab_chord_labs_path(t) for t in song.full_tab_paths]
    expected_best_symbolic_paths = []
    if well_aligned_midis:
        expected_best_symbolic_paths.append(
            filehandler.get_full_midi_chord_labs_path(*filehandler.get_expected_best_midi(song)))
    if [filehandler.get_full_tab_chord_labs_path(t) for t in song.full_tab_paths]:
        expected_best_symbolic_paths.append(
            filehandler.get_full_tab_chord_labs_path(filehandler.get_expected_best_tab_lab(song)))

    # Remove non-existing files (e.g. tab files in which too little chords were observed)
    all_symbolic_labs = [lab for lab in all_symbolic_labs if filehandler.file_exists(lab)]
    expected_best_symbolic_paths = [lab for lab in expected_best_symbolic_paths if filehandler.file_exists(lab)]

    # Get list of audio lab files
    audio_labs = song.full_mirex_chord_lab_paths
    audio_labs['CHF_2017'] = song.full_chordify_chord_labs_path

    # Sample every 10ms, so 100 samples per second
    song_duration = song.duration
    nr_of_samples = int(ceil(song_duration * 100))

    # Turn the chords list (a list of (key, mode-str, chroma-list) tuples) into an alphabet (a list of strings)
    alphabet = _chords_list_to_alphabet(chords_list)

    # Iterate over the two types of selection (all / best)
    for lab_list_i in [0, 1]:
        lab_list = [all_symbolic_labs, expected_best_symbolic_paths][lab_list_i]
        selection_name = ['all', 'best'][lab_list_i]
        lab_list = [i for i in lab_list if i != '']

        # Fill a numpy array with chord labels for each of the lab files
        chord_matrix = np.zeros((len(lab_list) + 1, nr_of_samples), dtype=int)
        for lab_nr in range(len(lab_list)):
            load_lab_file_into_chord_matrix(lab_list[lab_nr], lab_nr, chord_matrix, alphabet, nr_of_samples)

        # Iterate over the audio types:
        for audio_name, audio_lab in audio_labs.items():
            if filehandler.file_exists(audio_lab):
                # Add the lab file to our chord matrix
                load_lab_file_into_chord_matrix(audio_lab, len(lab_list), chord_matrix, alphabet, nr_of_samples)
                # Iterate over the three combination types; calculate labels and write them:
                final_labels_random = _random_chord_label_combination(chord_matrix, nr_of_samples)
                final_labels_majority = _majority_vote_chord_label_combination(chord_matrix, nr_of_samples, alphabet)
                final_labels_data_fusion = _data_fusion_chord_label_combination(chord_matrix, nr_of_samples, alphabet)
                _write_final_labels(final_labels_random,
                                    filehandler.get_data_fusion_path(song.key, 'rnd', selection_name, audio_name),
                                    alphabet)
                _write_final_labels(final_labels_majority,
                                    filehandler.get_data_fusion_path(song.key, 'mv', selection_name, audio_name),
                                    alphabet)
                _write_final_labels(final_labels_data_fusion,
                                    filehandler.get_data_fusion_path(song.key, 'df', selection_name, audio_name),
                                    alphabet)
