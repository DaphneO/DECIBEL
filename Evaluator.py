import mir_eval
import FileHandler


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
    score_root = mir_eval.chord.weighted_accuracy(comparisons_root, durations)
    comparisons_maj_min = mir_eval.chord.majmin(ref_labels, est_labels)
    score_maj_min = mir_eval.chord.weighted_accuracy(comparisons_maj_min, durations)
    comparisons_sevenths = mir_eval.chord.sevenths(ref_labels, est_labels)
    score_sevenths = mir_eval.chord.weighted_accuracy(comparisons_sevenths, durations)

    # if score_root < score_maj_min:
    #     stop = True # TODO: Make sure that this never happens
    return score_root, score_maj_min, score_sevenths


def add_data_fusion_evaluation(all_songs):
    with open(FileHandler.DATA_FUSION_RESULTS_PATH, 'w') as write_file:
        for song_key in all_songs:
            song = all_songs[song_key]
            data_fusion_lab_path = FileHandler.get_data_fusion_path(song_key)
            if song.full_ground_truth_chord_labs_path != '':
                s1, s2, _ = evaluate(song.full_ground_truth_chord_labs_path, data_fusion_lab_path)
                write_file.write('{0};{1};{2};{3}\n'.format(str(song_key), str(song.duration), str(s1), str(s2)))
                song.results.append(['data fusion', 1, data_fusion_lab_path, s1, s2])


def evaluate_all_songs(all_songs):
    # MIDI
    with open(FileHandler.MIDILABS_RESULTS_PATH, 'w') as write_file:
        probabilities_per_midi_name = dict()
        with open(FileHandler.MIDILABS_CHORD_PROBABILITY_PATH, 'r') as read_chord_probabilities:
            lines = read_chord_probabilities.readlines()
        for line in lines:
            parts = line.split(' ')
            probabilities_per_midi_name[parts[0]] = float(parts[1])
        for song_key in all_songs:
            song = all_songs[song_key]
            midi_index = 1
            for midi_lab_path in song.midi_labs:
                midi_name = FileHandler.get_file_name_from_full_path(midi_lab_path)

                # Find alignment score
                alignment_score = 0
                for a in song.midi_alignments:
                    if a.midi == FileHandler.get_full_synthesized_midi_path(midi_name):
                        alignment_score = a.score

                # Calculate CSR and write
                s1, s2, _ = evaluate(song.full_ground_truth_chord_labs_path, midi_lab_path)
                write_file.write('{0};{1};{2};{3};{4};{5};{6}\n'.format(str(song_key), str(song.duration),
                                                                        str(midi_name), str(alignment_score),
                                                                        str(probabilities_per_midi_name[midi_name]),
                                                                        str(s1), str(s2)))
                song.results.append(['midi', midi_index, midi_lab_path, s1, s2, alignment_score,
                                     probabilities_per_midi_name[midi_name]])
                midi_index += 1
    # Chordify
    with open(FileHandler.CHORDIFY_RESULTS_PATH, 'w') as write_file:
        for song_key in all_songs:
            song = all_songs[song_key]
            chordify_lab_path = song.full_chordify_chord_labs_path
            if song.full_ground_truth_chord_labs_path != '':
                s1, s2, _ = evaluate(song.full_ground_truth_chord_labs_path, chordify_lab_path)
                write_file.write('{0};{1};{2};{3}\n'.format(str(song_key), str(song.duration), str(s1), str(s2)))
                song.results.append(['chordify', 1, chordify_lab_path, s1, s2])

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
                tab_chord_path = FileHandler.get_chords_from_tab_filename(tab_path)
                tab_write_path = tab_chord_path.replace('ChordsFromTabs', 'TabLabs').replace('.npy', '.txt')
                if FileHandler.file_exists(tab_write_path):
                    s1, s2, _ = evaluate(song.full_ground_truth_chord_labs_path, tab_write_path)
                    write_file.write('{0};{1};{2};{3};{4};{5};{6}\n'.format(str(song_key), str(song.duration),
                                                                            str(tab_write_path),
                                                                            str(all_transpositions[tab_write_path]),
                                                                            str(all_likelihoods[tab_write_path]),
                                                                            str(s1), str(s2)))
                    song.results.append(['tab', tab_index, tab_write_path, s1, s2, all_transpositions[tab_write_path],
                                         all_likelihoods[tab_write_path]])
                    tab_index += 1
