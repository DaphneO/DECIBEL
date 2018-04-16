import FileHandler
import LabelParser.HarteLabelParser as HaLaPa
import ChordTemplateGenerator
import AudioMIDIAligner.PureAligner as AuMiAl

all_songs = FileHandler.get_all_songs()

# Extract Harte Labels for each song
HaLaPa.add_harte_labels(all_songs)

print("Start alignment")

# Align MIDIs to each song
AuMiAl.align_midis(all_songs)

ALL_CHORDS_LIST = ChordTemplateGenerator.generate_chroma_major_minor_sevenths()


i = 9