from math import ceil
from os import path

import numpy as np

from decibel.import_export.chord_annotation_io import import_chord_annotation
from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_alphabet import ChordAlphabet
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from decibel.import_export import filehandler
from decibel.import_export.midi_alignment_score_io import read_chord_alignment_score


def get_well_aligned_midis(song: Song) -> [str]:
    """
    Return names of only the well-aligned MIDIs for this Song (excluding duplicates)

    :param song: Song in our data set
    """
    # Find duplicate MIDIs in this song; we will exclude them
    duplicate_midis = filehandler.find_duplicate_midis(song)

    well_aligned_midis = []
    for full_midi_path in song.full_midi_paths:
        midi_name = filehandler.get_file_name_from_full_path(full_midi_path)
        if midi_name not in duplicate_midis:
            alignment_score = read_chord_alignment_score(midi_name)
            if alignment_score.is_well_aligned:
                well_aligned_midis.append(midi_name)

    return well_aligned_midis


def get_expected_best_midi(song: Song) -> (str, str):
    """
    Find name of the expected best well-aligned MIDI and segmentation type for this Song
    (based on MIDI chord probability)

    :param song: Song in our data set
    """
    # We only consider well-aligned MIDIs
    well_aligned_midis = get_well_aligned_midis(song)

    # Return path to the best MIDI of the song
    best_midi_name, best_midi_quality, best_segmentation = '', -9999999999, ''
    for segmentation_type in 'bar', 'beat':
        for full_midi_path in well_aligned_midis:
            midi_name = filehandler.get_file_name_from_full_path(full_midi_path)
            midi_chord_probability = filehandler.read_midi_chord_probability(segmentation_type, midi_name)
            if midi_chord_probability > best_midi_quality:
                # This is the best MIDI & segmentation type we have seen until now
                best_midi_name, best_midi_quality, best_segmentation = \
                    midi_name, midi_chord_probability, segmentation_type

    return best_midi_name, best_segmentation


def get_expected_best_tab_lab(song: Song) -> str:
    """
    Find the lab file of the expected best tab for this Song (based on log-likelihood returned by Jump Alignment)

    :param song: Song in our data set
    """
    best_tab_lab, best_tab_quality = '', 0

    for tab_path in song.full_tab_paths:
        tab_write_path = filehandler.get_full_tab_chord_labs_path(tab_path)
        if filehandler.file_exists(tab_write_path):
            tab_quality, _ = filehandler.read_log_likelihood(song.key, tab_path)
            if tab_quality > best_tab_quality:
                best_tab_lab, best_tab_quality = tab_write_path, tab_quality

    return best_tab_lab


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
    chord_annotation = import_chord_annotation(lab_path)
    for chord_annotation_item in chord_annotation.chord_annotation_items:
        chord_label_alphabet_index = alphabet.get_index_of_chord_in_alphabet(chord_annotation_item.chord)
        for s in range(int(chord_annotation_item.from_time * 100),
                       min(int(chord_annotation_item.to_time * 100), nr_of_samples - 1)):
            chord_matrix[i, s] = chord_label_alphabet_index


def data_fuse_song(song: Song, chord_vocabulary: ChordVocabulary):
    """
    Data fuse a song using all combinations of selection and combination methods, write the final labels to .lab files

    :param song: The song on which we want to apply data fusion
    :param chord_vocabulary: The chord vocabulary
    """
    # Check if data fusion has already been calculated  TODO: make this check more robust
    if path.isfile(filehandler.get_data_fusion_path(song.key, 'df', 'best', 'CHF_2017')):
        return

    # Get list of symbolic lab files (all / expected best)
    well_aligned_midis = get_well_aligned_midis(song)
    all_symbolic_lab_paths = \
        [filehandler.get_full_midi_chord_labs_path(wam, 'bar') for wam in well_aligned_midis] + \
        [filehandler.get_full_midi_chord_labs_path(wam, 'beat') for wam in well_aligned_midis] + \
        [filehandler.get_full_tab_chord_labs_path(t) for t in song.full_tab_paths]
    expected_best_symbolic_lab_paths = []
    if well_aligned_midis:
        expected_best_symbolic_lab_paths.append(
            filehandler.get_full_midi_chord_labs_path(*get_expected_best_midi(song)))
    if [filehandler.get_full_tab_chord_labs_path(t) for t in song.full_tab_paths]:
        expected_best_symbolic_lab_paths.append(
            filehandler.get_full_tab_chord_labs_path(get_expected_best_tab_lab(song)))

    # Remove non-existing files (e.g. tab files in which too little chords were observed)
    all_symbolic_lab_paths = [lab for lab in all_symbolic_lab_paths if filehandler.file_exists(lab)]
    expected_best_symbolic_lab_paths = [lab for lab in expected_best_symbolic_lab_paths if filehandler.file_exists(lab)]

    # Get list of audio lab files
    audio_labs = song.full_mirex_chord_lab_paths
    audio_labs['CHF_2017'] = song.full_chordify_chord_labs_path

    # Sample every 10ms, so 100 samples per second
    song_duration = song.duration
    nr_of_samples = int(ceil(song_duration * 100))

    # Turn the chords list (a list of (key, mode-str, chroma-list) tuples) into an chord_vocabulary (a list of strings)
    # alphabet = _chords_list_to_alphabet(chords_list) TODO remove if possible
    alphabet = ChordAlphabet(chord_vocabulary)

    # Iterate over the two types of selection (all / best)
    for lab_list_i in [0, 1]:
        lab_list = [all_symbolic_lab_paths, expected_best_symbolic_lab_paths][lab_list_i]
        lab_list = [i for i in lab_list if i != '']
        selection_name = ['all', 'best'][lab_list_i]

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
