import FileHandler
import AudioMIDIAligner.MIDISynthesizer as Synthesizer
import AudioMIDIAligner.PureAligner as AuMiAl
import ChordTemplateGenerator
import MIDIChordRecognizer.MIDIParser as MiChRe
from TabParser import TabParser, FeatureAndClassExtractor, HMM
import DataFusion
import Evaluator


def recognize_chords():
    # Make sure the file structure is ready
    FileHandler.init_folders()

    # Collect all songs and paths to their audio, MIDI and tab files, chord annotations and ground truth labels
    all_songs = FileHandler.get_all_songs()

    # Synthesize all MIDI files belonging to a song in all_songs and add paths to all_songs
    Synthesizer.synthesize_all_midis_to_wav(all_songs)

    # Align MIDIs to each song
    AuMiAl.align_midis(all_songs)

    # Find chords for each best aligned MIDI
    chords_list = ChordTemplateGenerator.generate_chroma_major_minor()
    MiChRe.classify_all_aligned_midis(all_songs, chords_list)
    duplicate_midis = MiChRe.find_duplicate_midis(all_songs)

    # Parse all tabs
    TabParser.classify_all_tabs(all_songs)

    # Extract or load all audio features
    FeatureAndClassExtractor.export_all_audio_features(all_songs)

    # Jump Alignment
    HMM.train_and_test(all_songs, chords_list)

    # Evaluate
    Evaluator.evaluate_all_songs(all_songs, duplicate_midis)

    for song_key in all_songs:
        if not FileHandler.file_exists(FileHandler.get_data_fusion_path(song_key, 'df', 'best', 'CHF')):
            DataFusion.data_fuse_song(all_songs[song_key], chords_list)

    Evaluator.add_data_fusion_evaluation(all_songs)

    # Data Fusion with different techniques
    # DataFusion.data_fuse_all_songs(all_songs, chords_list)
    #
    # # Add data fusion part in evaluation
    # Evaluator.add_data_fusion_evaluation(all_songs)
    #
    # # Final experiment: Data fusion with different audio chord estimation systems
    # DataFusion.data_fuse_all_songs_mirex(all_songs, chords_list)

    # Evaluate Data fusion with different audio chord estimation systems
    # Evaluator.add_mirex_data_fusion_evaluation(all_songs)

    return all_songs


# recognize_chords()
