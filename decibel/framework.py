import multiprocessing as mp

from sklearn.model_selection import KFold

from decibel.audio_midi_aligner import aligner
from decibel.audio_midi_aligner.alignment_parameters import AlignmentParameters
from decibel.audio_tab_aligner import feature_extractor, jump_alignment
from decibel.audio_tab_aligner.hmm_parameters import HMMParameters
from decibel.data_fusion import data_fusion
from decibel.evaluator import evaluator, result_table_generator, chord_label_visualiser, figure_generator
from decibel.import_export import filehandler
from decibel.midi_chord_recognizer import cassette
from decibel.midi_chord_recognizer.midi_bar_segmenter import MIDIBarSegmenter
from decibel.midi_chord_recognizer.midi_beat_segmenter import MIDIBeatSegmenter
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from decibel.tab_chord_parser import tab_parser

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
pool = mp.Pool(mp.cpu_count() - 1)  # use all available cores except one
for song_key in all_songs:
    pool.apply_async(prepare_song, args=(all_songs[song_key],), callback=print)
pool.close()
pool.join()
print('Pre-processing finished')

# # Train HMM parameters for jump alignment
# kf = KFold(n_splits=10, shuffle=True, random_state=42)
# hmm_parameter_dict = {}
# song_keys = list(all_songs.keys())
# for train_indices, test_indices in kf.split(all_songs):
#     hmm_parameters = jump_alignment.train(chord_vocabulary,
#                                           {song_keys[i]: all_songs[song_keys[i]] for i in list(train_indices)})
#     for test_index in test_indices:
#         song_key = song_keys[test_index]
#         hmm_parameter_dict[song_key] = hmm_parameters
#
# print('HMM parameter training finished')
#
#
# ####################
# # DEPLOYMENT PHASE #
# ####################
#
# def estimate_chords_of_song(song: Song, chord_vocab: ChordVocabulary, hmm_parameters_of_fold: HMMParameters):
#     # Align MIDIs to audio
#     alignment_parameters = AlignmentParameters()
#     aligner.align_single_song(song=song, alignment_parameters=alignment_parameters)
#
#     # Find chords for each best aligned MIDI
#     segmenters = [MIDIBarSegmenter(), MIDIBeatSegmenter()]
#     for segmenter in segmenters:
#         cassette.classify_aligned_midis_for_song(song=song, chord_vocabulary=chord_vocab, segmenter=segmenter)
#
#     # Jump alignment
#     jump_alignment.test_single_song(song=song, hmm_parameters=hmm_parameters_of_fold)
#
#     # Data fusion
#     data_fusion.data_fuse_song(song=song, chord_vocabulary=chord_vocab)  # TODO check: chord_vocabulary?
#
#     return '{} is estimated.'.format(str(song))
#
#
# # Estimate chords for all songs
# pool2 = mp.Pool(mp.cpu_count() - 1)  # use all available cores except one
# for song_key in all_songs:
#     pool2.apply_async(estimate_chords_of_song,
#                       args=(all_songs[song_key], chord_vocabulary, hmm_parameter_dict[song_key]),
#                       callback=print)
# pool2.close()
# pool2.join()
#
# print('Test phase (calculating labs of all methods) finished')
#
# ##############
# # Evaluation #
# ##############
#
# evaluator.evaluate_midis(all_songs)
# evaluator.evaluate_tabs(all_songs)
# evaluator.evaluate_song_based(all_songs)
#
# print('Evaluation finished!')
#
# ###############################
# # Generate tables and figures #
# ###############################
#
# # Generate lab visualisations for each song and audio method
# pool3 = mp.Pool(mp.cpu_count() - 1)  # use all available cores except one
# for song_key in all_songs:
#     for audio_method in ['CHF_2017'] + filehandler.MIREX_SUBMISSION_NAMES:
#         pool3.apply_async(chord_label_visualiser.export_result_image,
#                           args=(all_songs[song_key], chord_vocabulary, True, True, audio_method, True),
#                           callback=print)
# pool3.close()
# pool3.join()
# print("Visualisation finished!")
#
# # Export tables and figures used in the journal paper
# print('Table I: WCSR of AUDIO ACE SYSTEMS')
# print(result_table_generator.table_1_latex(all_songs))
# print('---------------------')
#
# print('Table II: RESULTS OF MIDI CHORD RECOGNITION FOR THE 50 MIDIS WITH THE LOWEST ALIGNMENT ERROR')
# print(result_table_generator.table_2_latex())
# print('---------------------')
#
# print('Table III: PERFORMANCE OF THREE MIDI SELECTION METHODS')
# print(result_table_generator.table_3_latex(all_songs))
# print('---------------------')
#
# print('Table IV: PERFORMANCE OF THREE TAB SELECTION METHODS')
# print(result_table_generator.table_4_latex(all_songs))
# print('---------------------')
#
# print('Table V: WCSR OF AUDIO ACE SYSTEMS AND DF-BEST')
# print(result_table_generator.table_5_latex(all_songs))
# print('---------------------')
# result_table_generator.print_wcsr_midi_information()
#
# figure_generator.figure_2()
# figure_generator.figure_3(all_songs)
