import pandas

from decibel.evaluator import evaluator
from decibel.import_export import filehandler


def compare_chord_labels(chord_label_1_path: str, chord_label_2_path: str):
    """
    Compare two chord label sequences

    :param chord_label_1_path: Path to .lab file of one chord label sequence
    :param chord_label_2_path: Path to .lab file of other chord label sequence
    :return: CSR (overlap percentage between the two chord label sequences)
    """
    return evaluator.evaluate(chord_label_1_path, chord_label_2_path)[0]


df_combination_and_selection_types = [('rnd', 'all'), ('mv', 'all'), ('df', 'all'),
                                      ('rnd', 'best'), ('mv', 'best'), ('df', 'best'),
                                      ('df', 'actual-best'),
                                      ('rnd', 'alltab'), ('rnd', 'besttab'),
                                      ('rnd', 'allmidi'), ('rnd', 'bestmidi'),
                                      ('mv', 'alltab'), ('mv', 'besttab'),
                                      ('mv', 'allmidi'), ('mv', 'bestmidi'),
                                      ('df', 'alltab'), ('df', 'besttab'),
                                      ('df', 'allmidi'), ('df', 'bestmidi')]


def print_overlap_audio_df_best(all_songs):
    print('Overlap audio and df-best on this audio')
    audio_types = ['CHF_2017'] + filehandler.MIREX_SUBMISSION_NAMES

    result = dict()

    for audio_type in audio_types:
        wcsr_numerator = 0
        wcsr_denominator = 0

        for song_key in all_songs:
            song = all_songs[song_key]

            if audio_type == 'CHF_2017':
                audio_lab_str = song.full_chordify_chord_labs_path
            else:
                audio_lab_str = filehandler.get_full_mirex_chord_labs_path(song, audio_type)
            df_lab_str = filehandler.get_data_fusion_path(song_key, 'DF', 'BEST', audio_type)

            if filehandler.file_exists(audio_lab_str) and filehandler.file_exists(df_lab_str):
                wcsr_numerator += compare_chord_labels(audio_lab_str, df_lab_str) * song.duration
                wcsr_denominator += song.duration

        print('Overlap between ' + audio_type + ' and ' + audio_type + '-DF-BEST (WCSR):' +
              str(wcsr_numerator / wcsr_denominator))

        result[audio_type] = wcsr_numerator / wcsr_denominator

    result_series = pandas.Series(result)
    return result_series


def print_overlap_audio_methods(all_songs):
    print('Overlap audio types (audio only)')

    result = dict()

    audio_types = ['CHF_2017'] + filehandler.MIREX_SUBMISSION_NAMES

    for audio_1 in audio_types:
        result[audio_1] = dict()
        for audio_2 in audio_types:
            wcsr_numerator = 0
            wcsr_denominator = 0

            for song_key, song in all_songs.items():
                if audio_1 == 'CHF_2017':
                    audio_1_lab = song.full_chordify_chord_labs_path
                else:
                    audio_1_lab = filehandler.get_full_mirex_chord_labs_path(song, audio_1)

                if audio_2 == 'CHF_2017':
                    audio_2_lab = song.full_chordify_chord_labs_path
                else:
                    audio_2_lab = filehandler.get_full_mirex_chord_labs_path(song, audio_2)

                if filehandler.file_exists(audio_1_lab) and filehandler.file_exists(audio_2_lab):
                    wcsr_numerator += compare_chord_labels(audio_1_lab, audio_2_lab) * song.duration
                    wcsr_denominator += song.duration

            result[audio_1][audio_2] = wcsr_numerator / wcsr_denominator

            print('Overlap between ' + audio_1 + ' and ' + audio_2 + ':' + str(wcsr_numerator / wcsr_denominator))

    result_df = pandas.DataFrame(result)
    return result_df


def print_overlap_df_best_methods(all_songs):
    print('Overlap audio types (df best)')

    result = dict()

    audio_types = ['CHF_2017'] + filehandler.MIREX_SUBMISSION_NAMES

    for audio_1 in audio_types:
        result[audio_1 + '-DF-BEST'] = dict()
        for audio_2 in audio_types:
            wcsr_numerator = 0
            wcsr_denominator = 0

            for song_key, song in all_songs.items():
                audio_1_df_lab = filehandler.get_data_fusion_path(song_key, 'DF', 'BEST', audio_1)
                audio_2_df_lab = filehandler.get_data_fusion_path(song_key, 'DF', 'BEST', audio_2)

                if filehandler.file_exists(audio_1_df_lab) and filehandler.file_exists(audio_2_df_lab):
                    wcsr_numerator += compare_chord_labels(audio_1_df_lab, audio_2_df_lab) * song.duration
                    wcsr_denominator += song.duration

            result[audio_1 + '-DF-BEST'][audio_2 + '-DF-BEST'] = wcsr_numerator / wcsr_denominator

            print('Overlap between ' + audio_1 + '-DF-BEST and ' + audio_2 + '-DF-BEST:' +
                  str(wcsr_numerator / wcsr_denominator))

    result_df = pandas.DataFrame(result)
    return result_df
