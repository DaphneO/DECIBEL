import FileHandler
import AudioMIDIAligner.MIDISynthesizer as Synthesizer
import AudioMIDIAligner.PureAligner as AuMiAl
import ChordTemplateGenerator
import MIDIChordRecognizer.MIDIParser as MiChRe
from TabParser import TabParser, FeatureAndClassExtractor, HMM
import DataFusion
import Evaluator


def recognize_chords():
    # Collect all songs and paths to their audio, MIDI and tab files, chord annotations and ground truth labels
    all_songs = FileHandler.get_all_songs()

    # Synthesize all MIDI files belonging to a song in all_songs and add paths to all_songs
    Synthesizer.synthesize_all_midis_to_wav(all_songs)

    # Align MIDIs to each song
    AuMiAl.align_midis(all_songs)

    # Find chords for each best aligned MIDI
    chords_list = ChordTemplateGenerator.generate_chroma_major_minor()
    MiChRe.classify_all_aligned_midis(all_songs, chords_list)

    # Parse all tabs
    TabParser.classify_all_tabs(all_songs)

    # Extract or load all audio features
    FeatureAndClassExtractor.export_all_audio_features(all_songs)

    # Jump Alignment
    HMM.train_and_test(all_songs, chords_list)

    # Evaluate
    Evaluator.evaluate_all_songs(all_songs)

    # Data Fusion
    DataFusion.data_fuse_all_songs(all_songs)

    # Add data fusion part in evaluation
    Evaluator.add_data_fusion_evaluation(all_songs)

    return all_songs

# recognize_chords()
