"""
This module generates the tables used in the paper.
"""
from decibel.import_export import filehandler
import pandas
import os.path as path


def write_tables(all_songs):
    with open(path.join(filehandler.TABLES_PATH, 'table_1.txt'), 'w') as write_file:
        write_file.write(table_1_latex())

    with open(path.join(filehandler.TABLES_PATH, 'table_2.txt'), 'w') as write_file:
        write_file.write(table_2_latex(all_songs))

    with open(path.join(filehandler.TABLES_PATH, 'table_3.txt'), 'w') as write_file:
        write_file.write(table_3_latex(all_songs))

    with open(path.join(filehandler.TABLES_PATH, 'table_4.txt'), 'w') as write_file:
        write_file.write(table_4_latex_with_best_midi_tab_only(all_songs))


def table_1_latex():
    """
    Export table 1 info to latex table.
    """
    with open(path.join(path.dirname(__file__), 'table_1_template.txt'), 'r') as file:
        template = file.read()

    data = _low_alignment_error_midi_wcsrs()

    latex_table = template.format(
        str(round(data['wcsr']['beat'] * 100, 1)),
        str(round(data['ovs']['beat'] * 100, 1)),
        str(round(data['uns']['beat'] * 100, 1)),
        str(round(data['seg']['beat'] * 100, 1)),
        str(round(data['wcsr']['bar'] * 100, 1)),
        str(round(data['ovs']['bar'] * 100, 1)),
        str(round(data['uns']['bar'] * 100, 1)),
        str(round(data['seg']['bar'] * 100, 1))
    )
    return latex_table


def _low_alignment_error_midi_wcsrs():
    """
    Get the chord estimation quality of the 50 best aligned MIDIs (used in table 1 of the paper)

    :return: Pandas data frame with the chord estimation quality (wcsr/ovs/uns/seg) of the 50 best aligned MIDIs
    """
    segmentation_methods = ['beat', 'bar']
    result = {}

    for segmentation_method in segmentation_methods:
        method_results = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS[segmentation_method], sep=';',
                                         names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
        top_method_results = method_results.sort_values('alignment_error', ascending=True).head(50)

        def get_weighted_performance(measure_str):
            total_duration = 0
            measure_duration = 0
            for midi_name in top_method_results.index:
                duration = top_method_results.loc[midi_name, 'duration']
                measure_value = top_method_results.loc[midi_name, measure_str]
                total_duration += duration
                measure_duration += (measure_value * duration)
            return measure_duration / total_duration

        measures = ['wcsr', 'ovs', 'uns', 'seg']

        result[segmentation_method] = {}
        for measure in measures:
            result[segmentation_method][measure] = get_weighted_performance(measure)

        if segmentation_method == 'bar':
            print('Alignment scores:')
            print(top_method_results['alignment_error'][0])
            print(top_method_results['alignment_error'][49])

    return pandas.DataFrame(result).transpose()


def table_2_latex(all_songs):
    d = _midi_selection_methods_table(all_songs)
    with open(path.join(path.dirname(__file__), 'table_2_template.txt'), 'r') as file:
        template = file.read()

    template_items = []
    for row_nr in range(5):
        for metric in ['wcsr', 'ovs', 'uns', 'seg']:
            for segmentation in ['beat', 'bar']:
                template_items.append(str(d[segmentation][metric][row_nr]))
    latex_table = template.format(*template_items)

    return latex_table


def _midi_selection_methods_table(all_songs):
    """
    Corresponds to Table II in the paper
    :param all_songs:
    :return:
    """
    segmentation_methods = ['beat', 'bar']
    result = {}
    for segmentation_method in segmentation_methods:
        # Read csv file with results for this segmentation method.
        all_method_results = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS[segmentation_method], sep=';',
                                             names=['song_key', 'duration', 'midi_name', 'alignment_error',
                                                    'template_sim',
                                                    'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
        # well_aligned_method_results = all_method_results[all_method_results['alignment_error'] <= 0.85]
        measures = ['wcsr', 'ovs', 'uns', 'seg']
        result[segmentation_method] = {}
        for measure in measures:
            total_duration = 0
            total_well_aligned_duration = 0

            min_csr_duration = 0
            avg_csr_duration = 0
            avg_well_aligned_duration = 0
            estimated_best_duration = 0
            max_csr_duration = 0

            for song_key in all_songs:
                song_duration = all_songs[song_key].duration

                if song_key in all_method_results['song_key'].values:
                    all_method_results_this_song = all_method_results[all_method_results.song_key == song_key]
                    well_aligned_method_results_this_song = \
                        all_method_results_this_song[all_method_results_this_song.alignment_error <= 0.85]

                    min_csr_index = all_method_results_this_song.wcsr.idxmin()
                    max_csr_index = all_method_results_this_song.wcsr.idxmax()

                    total_duration += song_duration
                    min_csr_duration += (song_duration * all_method_results_this_song[measure][min_csr_index])
                    avg_csr_duration += (song_duration * all_method_results_this_song[measure].mean())
                    max_csr_duration += (song_duration * all_method_results_this_song[measure][max_csr_index])
                    if not well_aligned_method_results_this_song.empty:
                        estimated_best_index = well_aligned_method_results_this_song.template_sim.idxmax()

                        total_well_aligned_duration += song_duration
                        avg_well_aligned_duration += \
                            (song_duration * well_aligned_method_results_this_song[measure].mean())
                        estimated_best_duration += \
                            (song_duration * well_aligned_method_results_this_song[measure][estimated_best_index])

            min_csr_duration /= total_duration
            avg_csr_duration /= total_duration
            avg_well_aligned_duration /= total_well_aligned_duration
            estimated_best_duration /= total_well_aligned_duration
            max_csr_duration /= total_duration
            result[segmentation_method][measure] = [round(min_csr_duration * 100, 1),
                                                    round(avg_csr_duration * 100, 1),
                                                    round(avg_well_aligned_duration * 100, 1),
                                                    round(estimated_best_duration * 100, 1),
                                                    round(max_csr_duration * 100, 1)]
    return pandas.DataFrame(result)


def table_3_latex(all_songs):
    """
    Export table III info to latex table

    :param all_songs: All songs in our data set
    """
    with open(path.join(path.dirname(__file__), 'table_3_template.txt'), 'r') as file:
        template = file.read()

    data = _tab_selection_methods_table(all_songs)

    latex_table = template.format(
        str(data['wcsr']['Worst CSR']),
        str(data['wcsr']['Average']),
        str(data['wcsr']['Best Log-likelihood']),
        str(data['wcsr']['Best CSR']),
    )
    return latex_table


def _tab_selection_methods_table(all_songs):
    """
    Corresponds to Table III in the paper

    :param all_songs: All songs in our data set
    :return:
    """
    method_results = pandas.read_csv(filehandler.TABLABS_RESULTS_PATH, sep=';',
                                     names=['song_key', 'duration', 'tab_name', 'likelihood', 'transposition',
                                            'wcsr', 'overseg', 'underseg', 'seg'])
    measures = ['wcsr', 'overseg', 'underseg', 'seg']
    result = {}
    for measure in measures:
        total_duration = 0
        min_csr_duration = 0
        avg_duration = 0
        max_csr_duration = 0
        max_likelihood_duration = 0
        for song_key in all_songs:
            if song_key in method_results['song_key'].values:
                duration = all_songs[song_key].duration
                method_results_this_song = method_results[method_results.song_key == song_key]
                lowest_csr_index = method_results_this_song.wcsr.idxmin()
                highest_csr_index = method_results_this_song.wcsr.idxmax()
                highest_likelihood_index = method_results_this_song.likelihood.idxmax()

                total_duration += duration
                min_csr_duration += (duration * method_results_this_song[measure][lowest_csr_index])
                avg_duration += (duration * method_results_this_song[measure].mean())
                max_csr_duration += (duration * method_results_this_song[measure][highest_csr_index])
                max_likelihood_duration += (duration * method_results_this_song[measure][highest_likelihood_index])
        min_csr_duration /= total_duration
        avg_duration /= total_duration
        max_csr_duration /= total_duration
        max_likelihood_duration /= total_duration
        result[measure] = [round(min_csr_duration * 100, 1),
                           round(avg_duration * 100, 1),
                           round(max_likelihood_duration * 100, 1),
                           round(max_csr_duration * 100, 1)]
    return pandas.DataFrame(result, index=['Worst CSR', 'Average', 'Best Log-likelihood', 'Best CSR'])


def table_4_latex(all_songs):
    """
    Export table 4 info to latex table.

    :param all_songs: all songs in the data set
    """
    with open(path.join(path.dirname(__file__), 'table_4_template.txt'), 'r') as file:
        template = file.read()

    differences = []

    def w(audio_method):
        original_wcsr = _get_wcsr(all_songs, audio_method)
        df_wcsr = _get_wcsr(all_songs, audio_method + '_DF-BEST')
        df_actual_best_wcsr = _get_wcsr(all_songs, audio_method + '_DF-ACTUAL-BEST')
        differences.append(df_wcsr - original_wcsr)
        return str(round(original_wcsr * 100, 1)) + '\\%&' + str(round(df_wcsr * 100, 1)) + '\\%&' + \
               str(round((df_wcsr - original_wcsr) * 100, 1)) + '\\%&' + str(
            round(df_actual_best_wcsr * 100, 1)) + '\\%'

    latex_table = template.format(w('CHF_2017'), w('CM2_2017'), w('JLW1_2017'), w('JLW2_2017'), w('KBK1_2017'),
                                  w('KBK2_2017'), w('WL1_2017'), w('JLCX1_2018'), w('JLCX2_2018'), w('SG1_2018'),
                                  w('CLSYJ1_2019'), w('HL2_2020'),
                                  str(round((sum(differences) / len(differences) * 100), 2)))
    return latex_table


def table_4_latex_with_best_midi_tab_only(all_songs):
    """
    Export table 4 info to latex table.

    :param all_songs: all songs in the data set
    """
    with open(path.join(path.dirname(__file__), 'table_4_with_best_midi_tab_only_template.txt'), 'r') as file:
        template = file.read()

    differences = []

    def w(audio_method):
        original_wcsr = _get_wcsr(all_songs, audio_method)
        df_wcsr = _get_wcsr(all_songs, audio_method + '_DF-BEST')
        df_actual_best_wcsr = _get_wcsr(all_songs, audio_method + '_DF-ACTUAL-BEST')
        df_midi_wcsr = _get_wcsr(all_songs, audio_method + '_DF-BESTMIDI')
        df_midi_tab = _get_wcsr(all_songs, audio_method + '_DF-BESTTAB')
        df_all_wcsr = _get_wcsr(all_songs, audio_method + '_DF-ALL')
        df_all_midi_wcsr = _get_wcsr(all_songs, audio_method + '_DF-ALLMIDI')
        df_all_tab_wcsr = _get_wcsr(all_songs, audio_method + '_DF-ALLTAB')
        differences.append(df_wcsr - original_wcsr)

        output_str = str(round(original_wcsr * 100, 1)) + '\\%&'
        for extra_result in [df_all_midi_wcsr, df_all_tab_wcsr, df_all_wcsr,
                             df_midi_wcsr, df_midi_tab, df_wcsr]:
            if extra_result > original_wcsr:
                output_str += '\\textbf{{' + str(round(extra_result * 100, 1)) + '\\%}}&'
            else:
                output_str += str(round(extra_result * 100, 1)) + '\\%&'
        output_str += str(round((df_wcsr - original_wcsr) * 100, 1)) + '\\%&'
        output_str += str(round(df_actual_best_wcsr * 100, 1)) + '\\%'

        return output_str

    latex_table = template.format(w('CHF_2017'), w('CM2_2017'), w('JLW1_2017'), w('JLW2_2017'), w('KBK1_2017'),
                                  w('KBK2_2017'), w('WL1_2017'), w('JLCX1_2018'), w('JLCX2_2018'), w('SG1_2018'),
                                  w('CLSYJ1_2019'), w('HL2_2020'),
                                  str(round((sum(differences) / len(differences) * 100), 2)))
    return latex_table


def _get_wcsr(all_songs, method_name):
    """
    Get the wcsr of estimating chords on all songs in our data set using a given method

    :param all_songs: All songs in our data set
    :param method_name: The method using which we estimate chords
    :return: WCSR of the estimation of chords on all songs in the data set, using the given method
    """
    method_results = pandas.read_csv(filehandler.get_evaluation_table_path(method_name), index_col=0)
    total_duration = 0
    wcsr_duration = 0
    for song_key in all_songs:
        if song_key in method_results.index:
            duration = all_songs[song_key].duration
            total_duration += duration
            wcsr_duration += (duration * method_results.loc[song_key, method_name + '_CSR'])
    return wcsr_duration / total_duration


def print_wcsr_midi_information():
    """
    Print information on the quality of MIDI files
    """
    segmentation_methods = ['beat', 'bar']
    for segmentation_method in segmentation_methods:
        # Read csv file with results for this segmentation method.
        method_results = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS[segmentation_method], sep=';',
                                         names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
        print('WCSR all MIDIs ' + segmentation_method + ': ' +
              str(round(sum(method_results.duration * method_results.wcsr) / sum(method_results.duration), 3)))

        well_aligned = method_results[method_results.alignment_error <= 0.85]
        print('WCSR well-aligned MIDIs ' + segmentation_method + ': ' +
              str(round(sum(well_aligned.duration * well_aligned.wcsr) / sum(well_aligned.duration), 3)))

        if segmentation_method == 'bar':
            print('Nr of MIDIs original: ' + str(method_results.shape[0]))
            print('Nr of MIDIs well-aligned: ' + str(well_aligned.shape[0]))
