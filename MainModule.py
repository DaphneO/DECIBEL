import FileHandler
import AudioMIDIAligner.MIDISynthesizer as Synthesizer
# import LabelParser.HarteLabelParser as HaLaPa
# import ChordTemplateGenerator
# import AudioMIDIAligner.PureAligner as AuMiAl

# Collect all songs and paths to their audio, MIDI and tab files
all_songs = FileHandler.get_all_songs()

# Synthesize all MIDI files belonging to a song in all_songs and add paths to all_songs
Synthesizer.synthesize_all_midis_to_wav(all_songs, FileHandler.SYNTHMIDI_FOLDER)

# # Extract Harte Labels for each song
# HaLaPa.add_harte_labels(all_songs)
#
# print("Start alignment")
#
# # Align MIDIs to each song
# AuMiAl.align_midis(all_songs)
#
# ALL_CHORDS_LIST = ChordTemplateGenerator.generate_chroma_major_minor_sevenths()


i = 9