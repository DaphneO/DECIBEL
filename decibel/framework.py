import multiprocessing as mp

from sklearn.model_selection import KFold

from decibel.audio_midi_aligner import aligner
from decibel.audio_midi_aligner.alignment_parameters import AlignmentParameters
from decibel.audio_tab_aligner import feature_extractor, jump_alignment
from decibel.audio_tab_aligner.hmm_parameters import HMMParameters
from decibel.data_fusion import data_fusion
from decibel.evaluator import evaluator, result_table_generator, chord_label_visualiser, figure_generator
from decibel.evaluator.chord_label_comparator import print_overlap_audio_df_best, print_overlap_audio_methods, \
    print_overlap_df_best_methods
from decibel.evaluator.chord_label_visualiser import export_result_image
from decibel.evaluator.result_table_generator import print_max_improvements
from decibel.import_export import filehandler, hmm_parameter_io
from decibel.midi_chord_recognizer import cassette
from decibel.midi_chord_recognizer.midi_bar_segmenter import MIDIBarSegmenter
from decibel.midi_chord_recognizer.midi_beat_segmenter import MIDIBeatSegmenter
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from decibel.tab_chord_parser import tab_parser


NR_CPU = max(mp.cpu_count() - 1, 1)

########################
# DATA SET PREPARATION #
########################

# Make sure the file structure is ready
filehandler.init_folders()

# Retrieve the chord vocabulary. Our experiments are running on a chord vocabulary of major and minor chords.
chord_vocabulary = ChordVocabulary.generate_chroma_major_minor()

# Collect all songs and paths to their audio, MIDI and tab files, chord annotations and ground truth labels
all_songs = filehandler.get_all_songs()

print('Preparing data set finished')


###############################
# TRAINING JUMP ALIGNMENT HMM #
###############################

def prepare_song(song: Song):
    tab_parser.classify_all_tabs_of_song(song=song)
    feature_extractor.export_audio_features_for_song(song=song)
    return '{} is preprocessed.'.format(str(song))


# Pre-process songs for (training) jump alignment
pool = mp.Pool(NR_CPU)
for song_key in all_songs:
    pool.apply_async(prepare_song, args=(all_songs[song_key],), callback=print)
pool.close()
pool.join()
print('Pre-processing finished')
# for song_key in all_songs:
#     prepare_song(all_songs[song_key])

# Train HMM parameters for jump alignment
kf = KFold(n_splits=10, shuffle=True, random_state=42)
hmm_parameter_dict = {}
song_keys = list(all_songs.keys())
for train_indices, test_indices in kf.split(all_songs):
    hmm_parameters_path = filehandler.get_hmm_parameters_path(train_indices)
    if filehandler.file_exists(hmm_parameters_path):
        hmm_parameters = hmm_parameter_io.read_hmm_parameters_file(hmm_parameters_path)
    else:
        hmm_parameters = jump_alignment.train(chord_vocabulary,
                                              {song_keys[i]: all_songs[song_keys[i]] for i in list(train_indices)})
        hmm_parameter_io.write_hmm_parameters_file(hmm_parameters, hmm_parameters_path)

    for test_index in test_indices:
        song_key = song_keys[test_index]
        hmm_parameter_dict[song_key] = hmm_parameters

print('HMM parameter training finished')


####################
# DEPLOYMENT PHASE #
####################

def estimate_chords_of_song(song: Song, chord_vocab: ChordVocabulary, hmm_parameters_of_fold: HMMParameters):
    # Align MIDIs to audio
    alignment_parameters = AlignmentParameters()
    aligner.align_single_song(song=song, alignment_parameters=alignment_parameters)

    # Find chords for each best aligned MIDI
    segmenters = [MIDIBarSegmenter(), MIDIBeatSegmenter()]
    for segmenter in segmenters:
        cassette.classify_aligned_midis_for_song(song=song, chord_vocabulary=chord_vocab, segmenter=segmenter)

    # Jump alignment
    jump_alignment.test_single_song(song=song, hmm_parameters=hmm_parameters_of_fold)

    # Data fusion
    data_fusion.data_fuse_song(song=song, chord_vocabulary=chord_vocab)

    return '{} is estimated.'.format(str(song))


# for song_key in all_songs:
#     estimate_chords_of_song(all_songs[song_key], chord_vocabulary, hmm_parameter_dict[song_key])

# Estimate chords for all songs
pool2 = mp.Pool(NR_CPU)
for song_key in all_songs:
    pool2.apply_async(estimate_chords_of_song,
                      args=(all_songs[song_key], chord_vocabulary, hmm_parameter_dict[song_key]),
                      callback=print)
pool2.close()
pool2.join()

print('Test phase (calculating labs of all methods) finished')

##############
# Evaluation #
##############

evaluator.evaluate_midis(all_songs)
evaluator.evaluate_tabs(all_songs)


def additional_actual_best_df_round(song: Song, chord_vocab: ChordVocabulary):
    data_fusion.data_fuse_song_with_actual_best_midi_and_tab(song=song, chord_vocabulary=chord_vocab)
    return '{} is data fused with actual best MIDI and tab.'.format(str(song))


pool3 = mp.Pool(NR_CPU)
for song_key in all_songs:
    pool3.apply_async(additional_actual_best_df_round,
                      args=(all_songs[song_key], chord_vocabulary),
                      callback=print)
pool3.close()
pool3.join()
# for song_key in all_songs:
#     additional_actual_best_df_round(all_songs[song_key], chord_vocabulary)

evaluator.evaluate_song_based(all_songs)

print('Evaluation finished!')

###############################
# Generate tables and figures #
###############################

# Generate lab visualisations for each song and audio method
all_method_names = ['CHF_2017','CM2_2017','JLW1_2017','JLW2_2017','KBK1_2017','KBK2_2017','WL1_2017','JLCX1_2018',
                        'JLCX2_2018','SG1_2018','CLSYJ1_2019','HL2_2020']
pool4 = mp.Pool(NR_CPU)
for song_key in all_songs:
    for audio_method in all_method_names:
        pool4.apply_async(chord_label_visualiser.export_result_image,
                          args=(all_songs[song_key], chord_vocabulary, True, True, audio_method, True),
                          callback=print)
pool4.close()
pool4.join()
print("Visualisation finished!")

# Export tables and figures used in the journal paper
result_table_generator.write_tables(all_songs)
result_table_generator.print_wcsr_midi_information()
figure_generator.export_figures(all_songs)

print_max_improvements(all_songs)

# audio_vs_df_best_overlaps = print_overlap_audio_df_best(all_songs)
# audio_vs_df_best_overlaps.to_csv('audio_vs_df_best_overlaps.csv')
# audio_overlaps = print_overlap_audio_methods(all_songs)
# audio_overlaps.to_csv('audio_overlaps.csv')
# df_best_overlaps = print_overlap_df_best_methods(all_songs)
# df_best_overlaps.to_csv('df_best_overlaps.csv')

# chord_label_visualiser.export_result_image(all_songs[165], chord_vocabulary, True, True, 'CHF_2017', True)
# chord_label_visualiser.export_result_image(all_songs[187], chord_vocabulary, True, True, 'CHF_2017', True)
# chord_label_visualiser.export_result_image(all_songs[197], chord_vocabulary, True, True, 'CHF_2017', True)
# chord_label_visualiser.export_result_image(all_songs[88], chord_vocabulary, True, True, 'CHF_2017', True)
# chord_label_visualiser.export_result_image(all_songs[167], chord_vocabulary, True, True, 'JLCX1_2018', True)


# for method in all_method_names:
#     chord_label_visualiser.export_result_image(all_songs[167], chord_vocabulary, True, True, method, True)
#     chord_label_visualiser.export_result_image(all_songs[135], chord_vocabulary, True, True, method, True)
#     chord_label_visualiser.export_result_image(all_songs[167], chord_vocabulary, True, True, method, True)
#     chord_label_visualiser.export_result_image(all_songs[87], chord_vocabulary, True, True, method, True)
#     chord_label_visualiser.export_result_image(all_songs[177], chord_vocabulary, True, True, method, True)
