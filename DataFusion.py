from math import ceil
import numpy as np
import ChordTemplateGenerator
import Chords
import FileHandler


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
        return 0  # Nog implementeren voor andere alphabets


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


def data_fuse_song(song, write_path):
    # Specify the paths to the .lab files we are going to fuse
    labs = [result[2] for result in song.results]

    song_duration = song.duration
    nr_of_samples = int(ceil(song_duration * 100))  # Sample every 10ms, so 100 samples per second

    chords_list = ChordTemplateGenerator.generate_chroma_major_minor()
    alphabet = chords_list_to_alphabet(chords_list)

    # Fill a numpy array with chord labels for each of the lab files
    chord_matrix = np.zeros((len(labs), nr_of_samples), dtype=int)
    for lab_nr in range(len(labs)):
        load_lab_file_into_chord_matrix(labs[lab_nr], lab_nr, chord_matrix, alphabet, nr_of_samples)

    # Calculate initial chord label probabilities
    chord_label_probabilities = np.empty((nr_of_samples, len(alphabet)))
    for sample_nr in range(nr_of_samples):
        for chord_nr in range(len(alphabet)):
            chord_label_probabilities[sample_nr, chord_nr] = \
                np.mean([chord_matrix[lab_nr, sample_nr] == chord_nr for lab_nr in range(len(labs))])

    # Calculate source accuracies
    for i in range(5):
        source_accuracies = np.empty(len(labs))
        for lab_nr in range(len(labs)):
            source_accuracies[lab_nr] = np.mean(
                [chord_label_probabilities[sample_nr, chord_matrix[lab_nr, sample_nr]] for sample_nr in range(nr_of_samples)])

        chord_label_probabilities = np.empty((nr_of_samples, len(alphabet)))
        for sample_nr in range(nr_of_samples):
            vote_counts = np.zeros(len(alphabet))
            for lab_nr in range(len(labs)):
                vote_counts[chord_matrix[lab_nr, sample_nr]] += source_accuracies[lab_nr]
            sum_exp_vote_counts_all_labels = sum([np.exp(vote_counts[chord_nr]) for chord_nr in range(len(alphabet))])
            for chord_nr in range(len(alphabet)):
                chord_label_probabilities[sample_nr, chord_nr] = \
                    np.exp(vote_counts[chord_nr]) / sum_exp_vote_counts_all_labels

    final_labels = np.empty(nr_of_samples, dtype=int)
    for sample_nr in range(nr_of_samples):
        final_labels[sample_nr] = np.argmax(chord_label_probabilities[sample_nr])

    # Write labels
    _write_final_labels(final_labels, write_path, alphabet)


def data_fuse_all_songs(all_songs):
    for song_key in all_songs:
        write_path = FileHandler.get_data_fusion_path(song_key)
        if not FileHandler.file_exists(write_path):
            data_fuse_song(all_songs[song_key], write_path)
