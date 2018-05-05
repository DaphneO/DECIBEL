import FileHandler
import AudioMIDIAligner.MIDISynthesizer as Synthesizer
import LabelParser.HarteLabelParser as HaLaPa
import AudioMIDIAligner.PureAligner as AuMiAl
import ChordTemplateGenerator
import MIDIChordRecognizer.MIDIParser as MiChRe
import Evaluator
from os import path

# Collect all songs and paths to their audio, MIDI and tab files
all_songs = FileHandler.get_all_songs()

# Extract Harte Labels for each song
HaLaPa.add_harte_labels(all_songs)

# Synthesize all MIDI files belonging to a song in all_songs and add paths to all_songs
Synthesizer.synthesize_all_midis_to_wav(all_songs, FileHandler.SYNTHMIDI_FOLDER)

# Align MIDIs to each song
AuMiAl.align_midis(all_songs)

# Find chords for each best aligned MIDI
CHORDS_LIST = ChordTemplateGenerator.generate_chroma_major_minor_sevenths()
MiChRe.classify_all_aligned_midis(all_songs, CHORDS_LIST)

# Evaluate
Evaluator.evaluate_all_songs(all_songs)


i = 9
