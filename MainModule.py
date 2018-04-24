import FileHandler
import AudioMIDIAligner.MIDISynthesizer as Synthesizer
import LabelParser.HarteLabelParser as HaLaPa
import AudioMIDIAligner.PureAligner as AuMiAl
import ChordTemplateGenerator
import MIDIChordRecognizer.MIDIParser as MiChRe
import mir_eval

# # Collect all songs and paths to their audio, MIDI and tab files
# all_songs = FileHandler.get_all_songs()
#
# # Extract Harte Labels for each song
# HaLaPa.add_harte_labels(all_songs)
#
# # Synthesize all MIDI files belonging to a song in all_songs and add paths to all_songs
# Synthesizer.synthesize_all_midis_to_wav(all_songs, FileHandler.SYNTHMIDI_FOLDER)
#
# # Align MIDIs to each song
# AuMiAl.align_midis(all_songs)
#
# # Find chords for each best aligned MIDI
# CHORDS_LIST = ChordTemplateGenerator.generate_chroma_major_minor()
# MiChRe.classify_all_aligned_midis(all_songs, CHORDS_LIST)

# Evaluate chords
(ref_intervals, ref_labels) = \
    mir_eval.io.load_labeled_intervals('E:\\Data\\ChordLabs\\01_-_Please_Please_Me\\03_-_Anna_(Go_To_Him).lab')
(est_intervals, est_labels) = \
    mir_eval.io.load_labeled_intervals('E:\\Data\\MIDIlabs\\003-003.lab')
est_intervals, est_labels = mir_eval.util.adjust_intervals(est_intervals, est_labels, ref_intervals.min(),
                                                           ref_intervals.max(), mir_eval.chord.NO_CHORD,
                                                           mir_eval.chord.NO_CHORD)
(intervals, ref_labels, est_labels) = \
    mir_eval.util.merge_labeled_intervals(ref_intervals, ref_labels, est_intervals, est_labels)
durations = mir_eval.util.intervals_to_durations(intervals)
comparisons = mir_eval.chord.root(ref_labels, est_labels)
score = mir_eval.chord.weighted_accuracy(comparisons, durations)

i = 9
