import mir_eval
import FileHandler
import numpy as np


def directional_hamming_distance(reference_intervals, estimated_intervals):
    est_ts = np.unique(estimated_intervals.flatten())
    seg = 0.
    for start, end in reference_intervals:
        dur = end - start
        between_start_end = est_ts[(est_ts >= start) & (est_ts < end)]
        seg_ts = np.hstack([start, between_start_end, end])
        seg += dur - np.diff(seg_ts).max()
    return seg / (reference_intervals[-1, 1] - reference_intervals[0, 0])


def evaluate(ground_truth_lab_path, my_lab_path):
    (ref_intervals, ref_labels) = \
        mir_eval.io.load_labeled_intervals(ground_truth_lab_path)
    (est_intervals, est_labels) = \
        mir_eval.io.load_labeled_intervals(my_lab_path)
    est_intervals, est_labels = mir_eval.util.adjust_intervals(est_intervals, est_labels, ref_intervals.min(),
                                                               ref_intervals.max(), mir_eval.chord.NO_CHORD,
                                                               mir_eval.chord.NO_CHORD)
    (intervals, ref_labels, est_labels) = \
        mir_eval.util.merge_labeled_intervals(ref_intervals, ref_labels, est_intervals, est_labels)
    durations = mir_eval.util.intervals_to_durations(intervals)
    comparisons_root = mir_eval.chord.root(ref_labels, est_labels)
    # score_root = mir_eval.chord.weighted_accuracy(comparisons_root, durations)
    comparisons_maj_min = mir_eval.chord.majmin(ref_labels, est_labels)
    score_maj_min = mir_eval.chord.weighted_accuracy(comparisons_maj_min, durations)
    # comparisons_sevenths = mir_eval.chord.sevenths(ref_labels, est_labels)
    # score_sevenths = mir_eval.chord.weighted_accuracy(comparisons_sevenths, durations)
    overseg = 1 - directional_hamming_distance(ref_intervals, est_intervals)
    underseg = 1 - directional_hamming_distance(est_intervals, ref_intervals)
    seg = min(overseg, underseg)

    # if score_root < score_maj_min:
    #     stop = True # TODO: Make sure that this never happens
    return score_maj_min, overseg, underseg, seg


# def add_data_fusion_evaluation(all_songs):
#     df_types = ['rand', 'mv', 'all', 'best']
#     with open(FileHandler.DATA_FUSION_RESULTS_PATH, 'w') as write_file:
#         for song_key in all_songs:
#             song = all_songs[song_key]
#             if song.full_ground_truth_chord_labs_path != '':
#                 # This song has ground truth, so we can evaluate it
#                 for data_fusion_type in df_types:
#                     data_fusion_lab_path = FileHandler.get_data_fusion_path(song_key, data_fusion_type)
#                     csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path, data_fusion_lab_path)
#                     song.results.append(['data fusion ' + data_fusion_type, 1,
#                                          data_fusion_lab_path, csr, overseg, underseg, seg])
#                 to_print = np.zeros(16)
#                 for result in song.results:
#                     if result[0].startswith('data fusion'):
#                         for df_type_id in range(len(df_types)):
#                             if result[0].endswith(df_types[df_type_id]):
#                                 to_print[4 * df_type_id], to_print[4 * df_type_id + 1], to_print[4 * df_type_id + 2], \
#                                 to_print[4 * df_type_id + 3] = result[3:7]
#                 write_file.write(str(song_key) + ';' + str(song.duration))
#                 for i in range(len(to_print)):
#                     write_file.write(';' + str(to_print[i]))
#                 write_file.write('\n')


def add_data_fusion_evaluation(all_songs):
    audio_types = ['CHF'] + FileHandler.MIREX2017_SUBMISSION_NAMES
    selection_names = ['all', 'best']
    df_types = ['rand', 'mv', 'df']

    with open(FileHandler.DATA_FUSION_RESULTS_PATH, 'w') as write_file:
        # Print title row
        write_file.write('KEY;LENGTH')
        for audio_type in audio_types:
            write_file.write(';{0}_CSR;{0}_OvS;{0}_UnS;{0}_SEG'.format(audio_type))
            for df_type in df_types:
                for selection_name in selection_names:
                    write_file.write(';{0}-{1}-{2}_CSR;{0}-{1}-{2}_OvS;{0}-{1}-{2}_UnS;{0}-{1}-{2}_SEG'.format(
                        df_type, selection_name, audio_type))
        write_file.write('\n')

        # Print data rows
        for song_key in all_songs:
            song = all_songs[song_key]
            if song.full_ground_truth_chord_labs_path != '':
                # This song has ground truth, so we can evaluate it
                write_file.write(str(song_key) + ';' + str(song.duration))
                # Iterate over the audio types
                for audio_type in audio_types:
                    if FileHandler.file_exists(FileHandler.get_full_mirex_2017_chord_labs_path(song, audio_type)):
                        # This song is labeled by this audio ACE system. First evaluate the original ACE system:
                        csr, overseg, underseg, seg = \
                            evaluate(song.full_ground_truth_chord_labs_path,
                                     FileHandler.get_full_mirex_2017_chord_labs_path(song, audio_type))
                        if audio_type != 'CHF':
                            song.results.append([audio_type, 1,
                                                 FileHandler.get_full_mirex_2017_chord_labs_path(song, audio_type),
                                                 csr, overseg, underseg, seg])
                        write_file.write(';{0};{1};{2};{3}'.format(str(csr), str(overseg), str(underseg), str(seg)))
                        # Now iterate over all data fusion types
                        for df_type in df_types:
                            for selection_name in selection_names:
                                data_fusion_lab_path = \
                                    FileHandler.get_data_fusion_path(song_key, df_type, selection_name, audio_type)
                                csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path,
                                                                       data_fusion_lab_path)
                                song.results.append([df_type.upper() + '-' + audio_type.upper(), 1,
                                                     data_fusion_lab_path, csr, overseg, underseg, seg])
                                write_file.write(
                                    ';{0};{1};{2};{3}'.format(str(csr), str(overseg), str(underseg), str(seg)))
                    else:
                        # Print a number of ';' for empty rows
                        for i in range(30):
                            write_file.write(';')
                write_file.write('\n')


def evaluate_all_songs(all_songs, duplicate_midis):
    # MIDI
    for segmentation_type in 'bar', 'beat':
        with open(FileHandler.MIDILABS_RESULTS_PATHS[segmentation_type], 'w') as write_file:
            probabilities_per_midi_name = dict()
            with open(FileHandler.MIDILABS_CHORD_PROBABILITY_PATHS[segmentation_type], 'r') as read_chord_probabilities:
                lines = read_chord_probabilities.readlines()
            for line in lines:
                parts = line.split(' ')
                probabilities_per_midi_name[parts[0]] = float(parts[1])
            for song_key in all_songs:
                song = all_songs[song_key]
                midi_index = 1
                for midi_lab_path in song.midi_labs:

                    midi_name = FileHandler.get_file_name_from_full_path(midi_lab_path)
                    if midi_name not in duplicate_midis and \
                            FileHandler.get_full_midi_chord_labs_path(midi_name, segmentation_type) == midi_lab_path:
                        # Find alignment score
                        alignment_score = 0
                        for a in song.midi_alignments:
                            if a.midi == FileHandler.get_full_synthesized_midi_path(midi_name):
                                alignment_score = a.score

                        # Calculate CSR and write
                        csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path, midi_lab_path)
                        write_file.write(
                            '{0};{1};{2};{3};{4};{5};{6};{7};{8}\n'.format(
                                str(song_key), str(song.duration), str(midi_name), str(alignment_score),
                                str(probabilities_per_midi_name[midi_name]),
                                str(csr), str(overseg), str(underseg), str(seg)))
                        song.results.append(['midi ' + segmentation_type, midi_index, midi_lab_path,
                                             csr, overseg, underseg, seg,
                                             alignment_score, probabilities_per_midi_name[midi_name]])
                        midi_index += 1
    # Chordify
    with open(FileHandler.CHORDIFY_RESULTS_PATH, 'w') as write_file:
        for song_key in all_songs:
            song = all_songs[song_key]
            chordify_lab_path = song.full_chordify_chord_labs_path
            if song.full_ground_truth_chord_labs_path != '':
                csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path, chordify_lab_path)
                write_file.write('{0};{1};{2};{3};{4};{5}\n'.format(str(song_key), str(song.duration),
                                                                    str(csr), str(overseg), str(underseg), str(seg)))
                song.results.append(['chordify', 1, chordify_lab_path, csr, overseg, underseg, seg])

    # Tabs
    with open(FileHandler.TABLABS_RESULTS_PATH, 'w') as write_file:
        with open(FileHandler.LOG_LIKELIHOODS_PATH, 'r') as read_likelihood:
            all_likelihoods = dict()
            all_transpositions = dict()
            for l in read_likelihood.readlines():
                tab_like_path, transposition, likelihood = l.rstrip().split(';')[1:4]
                all_likelihoods[tab_like_path] = likelihood
                all_transpositions[tab_like_path] = transposition
        for song_key in all_songs:
            song = all_songs[song_key]
            tab_index = 1
            for tab_path in song.full_tab_paths:
                # tab_chord_path = FileHandler.get_chords_from_tab_filename(tab_path)
                tab_write_path = FileHandler.get_full_tab_chord_labs_path(tab_path)
                # tab_write_path = tab_chord_path.replace('ChordsFromTabs', 'TabLabs').replace('.npy', '.txt')
                if FileHandler.file_exists(tab_write_path):
                    csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path, tab_write_path)
                    write_file.write('{0};{1};{2};{3};{4};{5};{6};{7};{8}\n'.format(
                        str(song_key), str(song.duration), str(tab_write_path), str(all_transpositions[tab_write_path]),
                        str(all_likelihoods[tab_write_path]), str(csr), str(overseg), str(underseg), str(seg)))
                    song.results.append(['tab', tab_index, tab_write_path, csr, overseg, underseg, seg,
                                         all_transpositions[tab_write_path], all_likelihoods[tab_write_path]])
                    tab_index += 1
