from math import ceil
import numpy as np
from decibel.utils import filehandler
from decibel.evaluator.evaluator import evaluate
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt


from decibel.data_fusion.data_fusion import load_lab_file_into_chord_matrix, _chords_list_to_alphabet


def _get_segmentation(song):
    """
    Get the segmentation of the sont (only for visualisation purposes)

    :param song: Song from which we want the segmentation information
    :return: Segmentation information (start time and description) from Isophonics dataset
    """
    segmentation_file_path = song.full_segmentation_labs_path
    result = []
    with open(segmentation_file_path, 'r') as read_file:
        input_lines = read_file.readlines()
        for input_line in input_lines:
            parts = input_line.split()
            result.append((float(parts[0]), parts[2].rstrip()))
    return result


def _show_chord_sequences(song, all_chords, best_indices, names, results, alphabet):
    """
    Return plot of chord sequences of this song

    :param song: Song for which we need the chord sequence visualisation
    :param all_chords: Chord matrix for each lab
    :param best_indices: Indices of best MIDI and tab
    :param names: Names of labs
    :param results: Evaluation results of labs
    :param alphabet: Chord vocabulary
    :return: Plot of chord sequences
    """
    # Information for legend
    all_chords.append(range(25))
    names.append('Legend')
    results.append('')

    # Prepare plot
    c_map = mpl.colors.ListedColormap(['#242424',
                                       '#FE2712', '#FC600A', '#FB9902', '#FCCC1A', '#FEFE33', '#B2D732', '#66B032',
                                       '#347C98', '#0247FE', '#4424D6', '#8601AF', '#C21460',
                                       '#7f0b01', '#7e2d01', '#7e4c01', '#7e6302', '#7f7f01', '#586a15', '#3a631c',
                                       '#214d5f', '#01227f', '#23126d', '#61017f', '#730c39'])
    fig, axes = plt.subplots(len(all_chords) + 1, figsize=(18, len(all_chords)))
    plt.suptitle(song.title.split(' - ')[-1] + ' (Index: ' + str(song.key) + ')', fontsize=25,
                 y=list(axes[0].get_position().bounds)[1] + 2 * list(axes[0].get_position().bounds)[3])

    # Add Chord Sequences (and legend) one by one
    for i in range(len(all_chords)):
        # Chord sequence bar
        new_chords = all_chords[i]
        new_chords = np.vstack((new_chords, new_chords))
        axes[i].imshow(new_chords, aspect='auto', cmap=c_map, vmin=0, vmax=24)

        # Text: name on left side, results (CSR, ovS, unS, Seg) on right side
        pos = list(axes[i].get_position().bounds)
        x_text = pos[0] - 0.01
        y_text = pos[1] + pos[3] / 2.
        if i in best_indices:
            fig.text(x_text, y_text, names[i], va='center', ha='right', fontsize=14, fontweight='bold')
        else:
            fig.text(x_text, y_text, names[i], va='center', ha='right', fontsize=14)
        fig.text(pos[0] + pos[2] + 0.01, y_text, results[i], va='center', ha='left', fontsize=14)

        # Remove axes
        axes[i].set_axis_off()

    # Add text to legend (note names for each color)
    for j in range(len(alphabet)):
        axes[len(all_chords) - 1].text(j, 0.5, alphabet[j], ha="center", va="center", color="w", fontsize=14)

    # Add segmentation bar
    segmentation = _get_segmentation(song)
    segment_starts = np.zeros(int(ceil(song.duration * 100)))
    for i in range(len(segmentation)):
        start_x = int(ceil(segmentation[i][0] * 100))
        for l in range(50):
            if start_x + l < len(segment_starts):
                segment_starts[start_x + l] = 1
        axes[len(all_chords)].text(start_x + 100, 0.2 + 0.6 * (i % 2), segmentation[i][1], va="center", fontsize=10)
    segment_starts = np.vstack((segment_starts, segment_starts))
    axes[len(all_chords)].imshow(segment_starts, aspect='auto', cmap='Greys')
    pos = list(axes[len(all_chords)].get_position().bounds)
    x_text = pos[0] - 0.01
    y_text = pos[1] + pos[3] / 2.
    fig.text(x_text, y_text, 'Segmentation', va='center', ha='right', fontsize=14)

    # Set song duration in seconds on x-axis
    ticks = [100 * x for x in range(int(song.duration) + 1)]
    ticks = [x for x in ticks if x % 1000 == 0]
    ticks.append(int(song.duration * 100))
    axes[len(all_chords)].set_xticks(ticks)
    axes[len(all_chords)].set_xticklabels([str(x / 100) for x in ticks])
    axes[len(all_chords)].get_yaxis().set_visible(False)

    return plt


def export_result_image(song, chords_list, midi=True, tab=True, audio='CHF_2017', df=True):
    """
    Export visualisation to a png file.

    :param song: Song for which we want to export the visualisation
    :param chords_list: Chord vocabulary
    :param midi: Show MIDI files?
    :param tab: Show Tab files?
    :param audio: Audio ACE method
    :param df: Show all DF results?
    """
    if filehandler.file_exists(filehandler.get_lab_visualisation_path(song, audio)):
        return song.title + " was already visualised for the ACE method " + audio + "."

    nr_of_samples = int(ceil(song.duration * 100))
    alphabet = _chords_list_to_alphabet(chords_list)

    # Select labs based on parameter setting
    label_data = [{'name': 'Ground truth', 'index': 0, 'lab_path': song.full_ground_truth_chord_labs_path,
                  'csr': 1.0, 'ovs': 1.0, 'uns': 1.0, 'seg': 1.0}]
    i = 1
    best_indices = []  # For expected best MIDI and tab
    if midi:
        duplicate_midis = filehandler.find_duplicate_midis(song)
        best_midi_name, best_segmentation = filehandler.get_expected_best_midi(song)
        full_midi_paths = song.full_midi_paths
        full_midi_paths.sort()
        for full_midi_path in full_midi_paths:
            midi_name = filehandler.get_file_name_from_full_path(full_midi_path)
            for segmentation_method in['bar', 'beat']:
                full_midi_chords_path = filehandler.get_full_midi_chord_labs_path(midi_name, segmentation_method)
                if filehandler.file_exists(full_midi_chords_path) \
                        and midi_name not in duplicate_midis:
                    # Evaluate song
                    csr, ovs, uns, seg = evaluate(song.full_ground_truth_chord_labs_path, full_midi_chords_path)
                    # Save evaluation values to label_data
                    label_data.append({'name': 'MIDI ' + midi_name + ' | ' + segmentation_method,
                                       'index': i, 'lab_path': full_midi_chords_path,
                                       'csr': csr, 'ovs': ovs, 'uns': uns, 'seg': seg})
                    # Check if this is the expected best MIDI & segmentation method for this song
                    if midi_name == best_midi_name and segmentation_method == best_segmentation:
                        best_indices.append(i)
                    i += 1

    if tab:
        best_tab = filehandler.get_expected_best_tab_lab(song)
        for tab_counter, full_tab_path in enumerate(song.full_tab_paths, 1):
            tab_chord_labs_path = filehandler.get_full_tab_chord_labs_path(full_tab_path)
            if filehandler.file_exists(tab_chord_labs_path):
                # Evaluate song
                csr, ovs, uns, seg = evaluate(song.full_ground_truth_chord_labs_path, tab_chord_labs_path)
                # Save evaluation values to label_data
                label_data.append({'name': 'Tab ' + str(tab_counter),
                                   'index': i, 'lab_path': tab_chord_labs_path,
                                   'csr': csr, 'ovs': ovs, 'uns': uns, 'seg': seg})
                if tab_chord_labs_path == best_tab:
                    best_indices.append(i)
                i += 1
    if df:
        csr, ovs, uns, seg = evaluate(song.full_ground_truth_chord_labs_path,
                                      filehandler.get_full_mirex_chord_labs_path(song, audio))
        label_data.append({'name': audio, 'index': i,
                           'lab_path': filehandler.get_full_mirex_chord_labs_path(song, audio),
                           'csr': csr, 'ovs': ovs, 'uns': uns, 'seg': seg})

        for selection_name in 'all', 'best':
            for combination_name in 'rnd', 'mv', 'df':
                df_lab_path = filehandler.get_data_fusion_path(song.key, combination_name, selection_name, audio)
                csr, ovs, uns, seg = evaluate(song.full_ground_truth_chord_labs_path, df_lab_path)
                label_data.append({'name': audio + '-' + combination_name.upper() + '-' + selection_name.upper(),
                                   'index': i, 'lab_path': df_lab_path,
                                   'csr': csr, 'ovs': ovs, 'uns': uns, 'seg': seg})

    # Fill a numpy array with chord labels for each of the lab files
    chord_matrix = np.zeros((len(label_data), nr_of_samples), dtype=int)
    for lab_nr in range(len(label_data)):
        load_lab_file_into_chord_matrix(label_data[lab_nr]['lab_path'], lab_nr, chord_matrix, alphabet, nr_of_samples)

    all_chords = [chord_matrix[x] for x in range(len(label_data))]

    # Find names
    names = [label_dict['name'] for label_dict in label_data]

    # Find results
    results = ['CSR  OvS  UnS  Seg']
    for label_dict in label_data[1:]:
        results.append(' '.join([str(round(label_dict[measure], 2)).ljust(4, '0')
                                 for measure in ['csr', 'ovs', 'uns', 'seg']]))

    # Show result
    plt1 = _show_chord_sequences(song, all_chords, best_indices, names, results, alphabet)

    plt1.savefig(filehandler.get_lab_visualisation_path(song, audio), bbox_inches="tight", pad_inches=0)

    return song.title + " was visualised for the ACE method " + audio + "."
