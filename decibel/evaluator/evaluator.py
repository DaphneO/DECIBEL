import mir_eval
import pandas
import numpy as np
from os import path
from decibel.utils import filehandler
import multiprocessing as mp


def _directional_hamming_distance(reference_intervals, estimated_intervals):
    """
    Compute the directional hamming distance between the reference intervals and the estimated intervals

    :param reference_intervals: GT intervals
    :param estimated_intervals: Estimated intervals
    :return: Directional hamming distance between reference intervals and estimates intervals
    """
    est_ts = np.unique(estimated_intervals.flatten())
    seg = 0.
    for start, end in reference_intervals:
        dur = end - start
        between_start_end = est_ts[(est_ts >= start) & (est_ts < end)]
        seg_ts = np.hstack([start, between_start_end, end])
        seg += dur - np.diff(seg_ts).max()
    return seg / (reference_intervals[-1, 1] - reference_intervals[0, 0])


def evaluate(ground_truth_lab_path, my_lab_path):
    """
    Evaluate the chord label sequence in my_lab_path, compared to the ground truth sequence in ground_truth_lab_path

    :param ground_truth_lab_path: Path to .lab file of ground truth chord label sequence
    :param my_lab_path: Path to .lab file of estimated chord label sequence
    :return: CSR, over-segmentation, under-segmentation, segmentation
    """
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
    comparisons_maj_min = mir_eval.chord.majmin(ref_labels, est_labels)
    score_maj_min = mir_eval.chord.weighted_accuracy(comparisons_maj_min, durations)

    overseg = 1 - _directional_hamming_distance(ref_intervals, est_intervals)
    underseg = 1 - _directional_hamming_distance(est_intervals, ref_intervals)
    seg = min(overseg, underseg)

    return score_maj_min, overseg, underseg, seg


def evaluate_method(all_songs, method_name, get_lab_function):
    """
    Evaluate all songs from our data set for one specific chord estimation technique, for which you get the labels using
    get_lab_function

    :param all_songs: All songs in our data set
    :param method_name: Name of the method (e.g. 'CHF_2017_DF_BEST')
    :param get_lab_function: A function that takes the song and outputs the lab path
    :return: Pandas DataFrame with results
    """
    result_dict = dict()

    for song_key in all_songs:
        song = all_songs[song_key]
        if song.full_ground_truth_chord_labs_path != '' and path.isfile(get_lab_function(song)):
            # This song has a ground truth and an estimation, so we can evaluate it
            result_dict[song_key] = list(evaluate(song.full_ground_truth_chord_labs_path, get_lab_function(song)))

    result_df = pandas.DataFrame.from_dict(result_dict, orient='index',
                                           columns=[method_name + '_' + m for m in ['CSR', 'OvS', 'UnS', 'Seg']])

    return result_df


def write_method_evaluations(all_songs, method_name, get_lab_function):
    """
    Write evaluations for all songs from our data set that have not been evaluated yet.

    :param all_songs: All songs in our data set
    :param method_name: Name of the method (e.g. 'CHF_2017_DF_BEST')
    :param get_lab_function: A function that takes the song and outputs the lab path
    """

    evaluation_path = filehandler.get_evaluation_table_path(method_name)
    if not path.isfile(evaluation_path):
        evaluation_df = evaluate_method(all_songs, method_name, get_lab_function)
        evaluation_df.to_csv(evaluation_path)


def _evaluate_audio_type(all_songs, df_types, selection_names, audio_type):
    """
    Evaluate all songs and selected df_types and selection_names for the selected audio_type

    :param all_songs: All songs in our data set
    :param df_types: Data combination types to test (rnd/mv/df)
    :param selection_names: Data selection types to test (all/best)
    :param audio_type: Audio method to test (CHF_2017 or one of the MIREX methods)
    :return: String indicating if the evaluation succeeded
    """
    def get_lab_function(song):
        if audio_type == 'CHF_2017':
            return song.full_chordify_chord_labs_path
        else:
            return filehandler.get_full_mirex_chord_labs_path(song, audio_type)

    write_method_evaluations(all_songs, audio_type, get_lab_function)

    for df_type in df_types:
        for selection_name in selection_names:
            # Evaluate this method of combining audio, MIDI and tabs
            method_name = audio_type + '_' + df_type.upper() + '-' + selection_name.upper()
            write_method_evaluations(
                all_songs, method_name,
                lambda song: filehandler.get_data_fusion_path(song.key, df_type, selection_name, audio_type))

    return audio_type + ' was evaluated.'


def evaluate_song_based(all_songs):
    """
    Evaluate all songs in the data set in parallel

    :param all_songs: All song in the data set
    :return: Print statement indicating that the evaluation was finished
    """
    audio_types = ['CHF_2017'] + filehandler.MIREX_SUBMISSION_NAMES
    selection_names = ['all', 'best']
    df_types = ['rnd', 'mv', 'df']

    pool = mp.Pool(mp.cpu_count() - 1)  # use all available cores except one
    for audio_type in audio_types:
        pool.apply_async(_evaluate_audio_type, args=(all_songs, df_types, selection_names, audio_type), callback=print)
    pool.close()
    pool.join()
    print('Evaluation finished!')


def evaluate_midis(all_songs) -> None:
    """
    Evaluate all lab files based on MIDI alignment and chord estimation

    :param all_songs: All songs in the data set
    """
    for segmentation_type in 'bar', 'beat':
        result_csv_path = filehandler.MIDILABS_RESULTS_PATHS[segmentation_type]
        if not path.isfile(result_csv_path):
            # Results were not calculated yet
            with open(result_csv_path, 'w') as write_file:
                for song_key in all_songs:
                    song = all_songs[song_key]
                    for midi_path in song.full_midi_paths:
                        midi_name = filehandler.get_file_name_from_full_path(midi_path)
                        alignment_score = filehandler.read_chord_alignment_score(midi_name)
                        chord_probability = filehandler.read_midi_chord_probability(segmentation_type, midi_name)
                        midi_lab_path = filehandler.get_full_midi_chord_labs_path(midi_name, segmentation_type)

                        # Calculate CSR and write
                        csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path,
                                                               midi_lab_path)
                        write_file.write(
                            '{0};{1};{2};{3};{4};{5};{6};{7};{8}\n'.format(
                                str(song_key), str(song.duration), str(midi_name), str(alignment_score),
                                str(chord_probability),
                                str(csr), str(overseg), str(underseg), str(seg)))


def evaluate_tabs(all_songs) -> None:
    """
    Evaluate all lab files based on tab parsing and alignment.

    :param all_songs: All songs in our data set.
    """
    result_csv_path = filehandler.TABLABS_RESULTS_PATH
    if not path.isfile(result_csv_path):
        # Results were not calculated yet
        with open(result_csv_path, 'w') as write_file:
            for song_key in all_songs:
                song = all_songs[song_key]
                for tab_path in song.full_tab_paths:
                    tab_write_path = filehandler.get_full_tab_chord_labs_path(tab_path)
                    if filehandler.file_exists(tab_write_path):
                        likelihood, transposition = filehandler.read_log_likelihood(song_key, tab_write_path)
                        if filehandler.file_exists(tab_write_path):
                            csr, overseg, underseg, seg = evaluate(song.full_ground_truth_chord_labs_path,
                                                                   tab_write_path)
                            write_file.write('{0};{1};{2};{3};{4};{5};{6};{7};{8}\n'.format(
                                str(song_key), str(song.duration), str(filehandler.get_relative_path(tab_write_path)),
                                str(likelihood), str(transposition), str(csr), str(overseg), str(underseg), str(seg)))
