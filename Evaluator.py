import mir_eval
import FileHandler
from os import path


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
    return score_root, score_maj_min, score_sevenths


def evaluate_all_songs(all_songs):
    with open(FileHandler.MIDILABS_RESULTS_PATH, 'w') as write_file:
        for song_key in all_songs:
            song = all_songs[song_key]
            for midi_lab_path in song.midi_labs:
                midi_name = FileHandler.get_file_name_from_full_path(midi_lab_path)

                # Find alignment score
                alignment_score = 0
                for a in song.midi_alignments:
                    if a.midi == path.join(FileHandler.SYNTHMIDI_FOLDER, midi_name + '.wav'):
                        alignment_score = a.score

                # Calculate
                s1, s2, s3 = evaluate(song.full_chord_labs_path, midi_lab_path)
                write_file.write('{0};{1};{2};{3};{4}\n'.format(str(midi_name), str(alignment_score),
                                                                str(s1), str(s2), str(s3)))
