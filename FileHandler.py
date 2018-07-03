# -*- coding: utf-8 -*-
from os import path, listdir, makedirs
from sys import platform
import csv
from Song import Song
from Chords import Chord

# Find DATA_PATH
if platform == 'linux2':  # Lubuntu laptop
    DATA_PATH = "/media/daphne/Seagate Expansion Drive/Data"
else:  # Windows laptop
    DATA_PATH = "E:\Data"


def _full_path_to(folder_name, i_f_r):
    # type: (str, str) -> str
    """
    Helper method to find the full path to a folder in Data
    :param folder_name: Name of the folder in Data
    :param i_f_r: 'i' (Input), 'f' (Files) or 'r' (Results). 'r' has subfolders 'l' (Labs), 't' (Tables), 'f' (Figures)
    and 'v' (LabVisualisations)
    :return: Full path to the folder in Data
    >>> _full_path_to('MIDI', 'i')
    '/media/daphne/Seagate Expansion Drive/Data/Input/MIDI'
    """
    if i_f_r == 'i':
        parent_folder = 'Input'
    elif i_f_r == 'f':
        parent_folder = 'Files'
    else:
        parent_folder = 'Results'
        if i_f_r[1] == 'l':
            parent_folder = path.join(parent_folder, 'Labs')
        elif i_f_r[1] == 't':
            parent_folder = path.join(parent_folder, 'Tables')
        elif i_f_r[1] == 'f':
            parent_folder = path.join(parent_folder, 'Figures')
        else:
            parent_folder = path.join(parent_folder, 'LabVisualisations')
    return path.join(DATA_PATH, parent_folder, folder_name)


# Add folder to ground truth labels
CHORDLABS_FOLDER = _full_path_to('GT_ChordLabels', 'i')

# Add folders to our different representations and the index files with which we can find them
INDEX_PATH = _full_path_to('IndexAudio.csv', 'i')
TAB_INDEX_PATH = _full_path_to('IndexTabs.csv', 'i')
AUDIO_FOLDER = _full_path_to('Audio', 'i')
MIDI_FOLDER = _full_path_to('MIDI', 'i')
TABS_FOLDER = _full_path_to('Tabs', 'i')

# Folders to output of audio chord recognition algorithms
CHORDIFY_FOLDER = _full_path_to('ChordifyLabs', 'i')
MIREX2017_FOLDER = _full_path_to('MIREX2017Labs', 'i')
MIREX2017_SUBMISSION_NAMES = listdir(MIREX2017_FOLDER)

SOUND_FONT_PATH = _full_path_to('FluidR3_GM.sf2', 'i')

SYNTHMIDI_FOLDER = _full_path_to('SynthMIDI', 'f')
ALIGNMENTS_FOLDER = _full_path_to('Alignments', 'f')
AUDIO_FEATURES_FOLDER = _full_path_to('AudioFeatures', 'f')
CHORDS_FROM_TABS_FOLDER = _full_path_to('ChordsFromTabs', 'f')

MIDILABS_RESULTS_PATHS = {'bar': _full_path_to('MidiLabsResultsBar.csv', 'rt'),
                          'beat': _full_path_to('MidiLabsResultsBeat.csv', 'rt')}
CHORDIFY_RESULTS_PATH = _full_path_to('ChordifyResults.csv', 'rt')
MIREX2017_RESULTS_PATHS = dict()
for mirex_submission_name in MIREX2017_SUBMISSION_NAMES:
    MIREX2017_RESULTS_PATHS[mirex_submission_name] = _full_path_to(mirex_submission_name + 'Results.csv', 'rt')

MIDILABS_CHORD_PROBABILITY_PATHS = {'bar': _full_path_to('MidiLabsChordProbabilitiesBar.csv', 'f'),
                                    'beat': _full_path_to('MidiLabsChordProbabilitiesBeat.csv', 'f')}
TABLABS_RESULTS_PATH = _full_path_to('TabLabsResults.csv', 'rt')
LOG_LIKELIHOODS_PATH = _full_path_to('log_likelihoods.txt', 'f')
DUPLICATE_MIDI_PATH = _full_path_to('DuplicateMIDIs.txt', 'f')

# Folders for output chord label sequences for all three representation types
MIDILABS_FOLDERS = {'bar': _full_path_to('MIDIlabsBar', 'rl'), 'beat': _full_path_to('MIDIlabsBeat', 'rl')}
TABLABS_FOLDER = _full_path_to('TabLabs', 'rl')

DATA_FUSION_FOLDERS = dict()
for df_type in ['rand', 'mv', 'df']:
    for selection_method in ['all', 'best']:
        fn = df_type.upper() + '_' + selection_method.upper() + '_'
        DATA_FUSION_FOLDERS[fn + 'CHF'] = _full_path_to(fn + 'CHF', 'rl')
        for mirex_submission_name in MIREX2017_SUBMISSION_NAMES:
            DATA_FUSION_FOLDERS[fn + mirex_submission_name] = _full_path_to(fn + mirex_submission_name, 'rl')
DATA_FUSION_RESULTS_PATH = _full_path_to('DataFusionResults.csv', 'rt')


def init_folders():
    needed_folders = [SYNTHMIDI_FOLDER, ALIGNMENTS_FOLDER, AUDIO_FEATURES_FOLDER, CHORDS_FROM_TABS_FOLDER,
                      MIDILABS_FOLDERS['bar'], MIDILABS_FOLDERS['beat'], TABLABS_FOLDER,
                      _full_path_to('', 'rt'), _full_path_to('', 'rf'), _full_path_to('', 'rv')]
    for folder_name in DATA_FUSION_FOLDERS:
        needed_folders.append(DATA_FUSION_FOLDERS[folder_name])
    for needed_folder in needed_folders:
        if not path.isdir(needed_folder):
            makedirs(needed_folder)


def get_all_songs():
    """
    Find a dictionary of Song objects, indexed by integer keys. Key, title, album, ground truth chord labels,
    audio path and Chordify labels path are already added to each song.
    :return: Dictionary of Songs in our data set.
    """
    # Import all songs, assign full paths
    all_songs = dict()
    with open(INDEX_PATH, 'rb') as index_csv:
        index_csv_reader = csv.reader(index_csv, delimiter=';')
        for key_data_row in index_csv_reader:
            if len(key_data_row) >= 4:
                key = int(key_data_row[0])
                title = key_data_row[1]
                album = key_data_row[2]
                full_chord_labs_path = get_full_chord_labs_path(key_data_row[3])
                all_songs[key] = Song(key, title, album, full_chord_labs_path, get_full_audio_path(key))
    # Find corresponding tabs
    with open(TAB_INDEX_PATH, 'r') as tab_index_csv:
        tab_index_csv_reader = csv.reader(tab_index_csv, delimiter=';')
        for tab_data_row in tab_index_csv_reader:
            if len(tab_data_row) >= 4:
                key = int(tab_data_row[2])
                if key in all_songs:
                    tab_path = tab_data_row[3]
                    all_songs[key].add_tab_path(path.join(TABS_FOLDER, tab_path))
    # Find corresponding MIDIs
    all_midis = _get_midi_path_list()
    for midi_file_name in all_midis:
        key = int(midi_file_name.split('-')[0])
        if key in all_songs:
            all_songs[key].add_midi_path(path.join(MIDI_FOLDER, midi_file_name))
    # Find labs from Audio Chord Estimation systems
    for song_key in all_songs:
        # Chordify
        all_songs[song_key].full_chordify_chord_labs_path = get_full_chordify_chord_labs_path(song_key)
        # MIREX2017
        for mirex_submission_name in MIREX2017_SUBMISSION_NAMES:
            all_songs[song_key].full_mirex_2017_chord_lab_paths[mirex_submission_name] = \
                get_full_mirex_2017_chord_labs_path(all_songs[song_key], mirex_submission_name)
    return all_songs


def get_full_chord_labs_path(chord_labs_path):
    # type: (str) -> str
    """
    Get the full path to the file in the ChordLabs folder
    :param chord_labs_path: not-full path to chord labs file
    :return: Full path to chord labs file
    """
    if chord_labs_path == '':
        return ''
    chord_labs_path_parts = chord_labs_path.split('\\')
    return path.join(CHORDLABS_FOLDER, chord_labs_path_parts[0], chord_labs_path_parts[1], chord_labs_path_parts[2])


def get_full_chordify_chord_labs_path(key):
    # type: (int) -> str
    """
    Get the full path to the Chordify chord labels, given the key of a song
    :param key: The key of the song from which we need the Chordify chord labels
    :return: Full path to the Chordify chord labels of our song
    """
    return path.join(CHORDIFY_FOLDER, str(key) + '.txt')


def get_full_mirex_2017_chord_labs_path(song, mirex_submission_name):
    # type: (Song, str) -> str
    if mirex_submission_name == 'CHF':  # Chordify
        return get_full_chordify_chord_labs_path(song.key)
    return song.full_ground_truth_chord_labs_path.replace('GT_ChordLabels', 'MIREX2017Labs/' + mirex_submission_name)


def get_full_midi_chord_labs_path(midi_file_name, segmentation_type):
    # type: (str, str) -> str
    """
    Get the full path to the MIDI chord labels, given the midi file name
    :param midi_file_name: File name (not a full path!) to our MIDI file
    :param segmentation_type: Either 'bar' or 'beat'
    :return: Full path to the MIDI chord labels of our MIDI
    """
    return path.join(MIDILABS_FOLDERS[segmentation_type], midi_file_name + '.lab')


def get_full_tab_chord_labs_path(full_tab_file_path):
    # type: (str) -> str
    """
    Get the full path to the tab chord labels, given the full path to the tab file
    :param full_tab_file_path: Tab file
    :return: Full path to the tab chord labels of our song
    """
    filename = get_file_name_from_full_path(full_tab_file_path)
    return path.join(TABLABS_FOLDER, filename + '.txt')


def get_full_audio_path(key):
    # type: (int) -> str
    """
    Get the full path to the .wav file, given the key of a song
    :param key: The key of the song from which we need the audio
    :return: Full path to the audio of our song
    """
    return path.join(AUDIO_FOLDER, str(key) + '.wav')


def get_full_synthesized_midi_path(midi_file_name):
    # type: (str) -> str
    """
    Get the full path to the .wav file that is a synthesized version of the MIDI specified by midi_file_name
    :param midi_file_name: File name (not a full path!) to our MIDI file
    :return: Full path to the .wav file that is a synthesized version of our MIDI
    """
    return path.join(SYNTHMIDI_FOLDER, midi_file_name + '.wav')


def get_full_midi_path(midi_file_name):
    # type: (str) -> str
    """
    Get the full path to the .mid file of the MIDI specified by midi_file_name
    :param midi_file_name: File name (not a full path!) to our MIDI file
    :return: Full path to the .mid file of our MIDI
    """
    return path.join(MIDI_FOLDER, midi_file_name + '.mid')


def get_full_alignment_path(midi_file_name):
    # type: (str) -> str
    """
    Get the full path to the .txt file of the alignment between our MIDI and the audio file it is matched to
    :param midi_file_name: File name (not a full path!) to our MIDI file
    :return: Full path to the .txt file that represents the alignment
    """
    return path.join(ALIGNMENTS_FOLDER, midi_file_name + '.txt')


def _get_midi_path_list():
    """
    Get a list with all .mid files in our MIDI folder
    :return: The list with all .mid files in our MIDI folder
    """
    result = []
    for midi_file in listdir(MIDI_FOLDER):
        if midi_file.endswith(".mid"):
            result.append(midi_file)
    return result


def get_file_name_from_full_path(full_path):
    # type: (str) -> str
    """
    Extract the file name (without extension) from a full path
    :param full_path: The full path we want to extract the file name from
    :return: The file name from our full path
    >>> get_file_name_from_full_path('/media/daphne/Seagate Expansion Drive/Data/MIDI/001-001.mid')
    '001-001'
    >>> get_file_name_from_full_path('/media/daphne/Seagate Expansion Drive/Data/MIDI/001-001.txt')
    '001-001'
    """
    return path.basename(full_path).split('.')[0]


def file_exists(full_path):
    # type: (str) -> bool
    """
    Shortcut method to check if a file, specified by its full path exists
    :param full_path: Full path to the file of which we want to know if it exists
    :return: Does our file exist already?
    """
    return path.isfile(full_path)


def get_chords_from_tab_filename(full_tab_file_path):
    # type: (str) -> str
    """
    Get the filename to write the parsed chords from the tab file
    :param full_tab_file_path: Tab file
    :return: Filename for parsed chords
    """
    filename = get_file_name_from_full_path(full_tab_file_path)
    return path.join(CHORDS_FROM_TABS_FOLDER, filename + '.npy')


def get_full_audio_features_path(key):
    # type: (int) -> str
    """
    Get the full path to the full audio features path of the song specified by the key
    :param key: Key of the song for which we need the audio features path
    :return: Audio features path of our song
    """
    return path.join(AUDIO_FEATURES_FOLDER, str(key) + '.npy')


def get_data_fusion_path(key, df_type, selection_method, audio_ace):
    # type: (int, str) -> str
    """
    Get the full path to the data fusion labels path of the song specified by the key
    :param key: Key of the song for which we need the data fusion labels path
    :param df_type: Which type of data fusion; either 'rand', 'mv', 'df'
    :param selection_method: Do we use all labels or only the expected best?
    :param audio_ace: Which audio algorithm did we use (CHF or one of the MIREX algorithms)
    :return: Data fusion labels path of our song
    """
    return path.join(DATA_FUSION_FOLDERS[df_type.upper() + '_' + selection_method.upper() + '_' + audio_ace],
                     str(key) + '.lab')



# def get_data_fusion_path(key, df_type):
#     # type: (int, str) -> str
#     """
#     Get the full path to the data fusion labels path of the song specified by the key
#     :param key: Key of the song for which we need the data fusion labels path
#     :param df_type: Which type of data fusion; either 'rand', 'mv', 'all' or 'best'
#     :return: Data fusion labels path of our song
#     """
#     return path.join(DATA_FUSION_FOLDERS[df_type], str(key) + '.lab')


# def get_mirex_data_fusion_path(key, df_type, audio_ace_name):
#     # type: (int, str, str) -> str
#     """
#     Get the full path to the data fusion labels path of the song specified by the key
#     :param key: Key of the song for which we need the data fusion labels path
#     :param df_type: Which type of data fusion; either 'rand', 'mv', 'all' or 'best'
#     :param audio_ace_name: Which audio system; either 'CHF', '' or one of the MIREX systems
#     :return: Data fusion labels path of our song
#     """
#     return path.join(DATA_FUSION_FOLDERS[df_type, audio_ace_name], str(key) + '.lab')
