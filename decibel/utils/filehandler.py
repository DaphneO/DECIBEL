# -*- coding: utf-8 -*-
from os import path, listdir, makedirs, remove
import csv
from decibel.utils.musicobjects import Song
import random


# Set random seed to enable reproducibility
random.seed(25)


# Read the path to the data folder. This path is in the 'data_path.txt' file
with open(path.join(path.dirname(__file__), 'data_path.txt'), 'r') as read_file:
    DATA_PATH = read_file.readline()


def _full_path_to(folder_name: str, i_f_r: str):
    """
    Helper method to find the full path to a folder in Data

    :param folder_name: Name of the folder in Data
    :param i_f_r: 'i' (Input), 'f' (Files) or 'r' (Results). 'r' has subfolders 'l' (Labs), 't' (Tables), 'f' (Figures)
    and 'v' (LabVisualisations)
    :return: Full path to the folder in Data
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


def _get_mirex_submissions(from_year: int):
    """
    Get all names and directory paths to MIREX submissions from previous years, starting from from_year

    :param from_year: First year for which we want to find the MIREX results
    :return: Tuple of all names and directory paths to MIREX submissions from previous years, starting from from_year
    """
    all_submission_names, all_mirex_folders = [], []
    from_year = max(from_year, 2013)  # There are no results before 2013
    mirex_folder = _full_path_to('MirexResults', 'i')
    years_in_folder = listdir(mirex_folder)
    for year_folder in years_in_folder:
        try:
            year = int(year_folder)
            if year >= from_year:
                # We want to test DECIBEL on this year's results!
                isophonics_results_folder = path.join(mirex_folder, year_folder, 'Isophonics2009')
                names = [name for name in listdir(isophonics_results_folder) if name != 'Ground-Truth']
                submission_names = [name + '_' + year_folder for name in names]
                all_submission_names = all_submission_names + submission_names
                mirex_folders = [path.join(isophonics_results_folder, name) for name in names]
                all_mirex_folders = all_mirex_folders + mirex_folders
        except ValueError:
            pass
    return all_submission_names, all_mirex_folders


# Add folder to ground truth labels
CHORDLABS_FOLDER = _full_path_to('GT_ChordLabels', 'i')
SEGMENTATION_LABS_FOLDER = _full_path_to('GT_SegmentationLabels', 'i')

# Add folders to our different representations and the index files with which we can find them
INDEX_PATH = _full_path_to('IndexAudio.csv', 'i')
TAB_INDEX_PATH = _full_path_to('IndexTabs.csv', 'i')
AUDIO_FOLDER = _full_path_to('Audio', 'i')
MIDI_FOLDER = _full_path_to('MIDI', 'i')
TABS_FOLDER = _full_path_to('Tabs', 'i')

# Folders to output of audio chord recognition algorithms
CHORDIFY_FOLDER = _full_path_to('ChordifyLabs', 'i')

# Names and folders of MIREX audio ACE results
MIREX_SUBMISSION_NAMES, MIREX_SUBMISSION_FOLDERS = _get_mirex_submissions(2017)

# We need the sound font for synthesizing MIDI files
SOUND_FONT_PATH = _full_path_to('FluidR3_GM.sf2', 'i')

# Folders where we save (large-sized/expensive to compute) temporary results
SYNTHMIDI_FOLDER = _full_path_to('SynthMIDI', 'f')
ALIGNMENTS_FOLDER = _full_path_to('Alignments', 'f')
AUDIO_FEATURES_FOLDER = _full_path_to('AudioFeatures', 'f')
CHORDS_FROM_TABS_FOLDER = _full_path_to('ChordsFromTabs', 'f')

# Paths to .csv files with results (CSR and segmentation measures for each song)
MIDILABS_RESULTS_PATHS = {'bar': _full_path_to('MidiLabsResultsBar.csv', 'rt'),
                          'beat': _full_path_to('MidiLabsResultsBeat.csv', 'rt')}
MIDILABS_CHORD_PROBABILITY_FOLDER = _full_path_to('MidiChordProbabilities', 'f')
MIDILABS_ALIGNMENT_SCORE_FOLDER = _full_path_to('MidiAlignmentScores', 'f')
LOG_LIKELIHOOD_FOLDER = _full_path_to('LogLikelihoods', 'f')

TABLABS_RESULTS_PATH = _full_path_to('TabLabsResults.csv', 'rt')
DUPLICATE_MIDI_PATH = _full_path_to('DuplicateMIDIs.txt', 'f')

# Folders for output chord label sequences for all three representation types
MIDILABS_FOLDERS = {'bar': _full_path_to('MIDIlabsBar', 'rl'), 'beat': _full_path_to('MIDIlabsBeat', 'rl')}
TABLABS_FOLDER = _full_path_to('TabLabs', 'rl')

DATA_FUSION_FOLDERS = dict()
for df_type in ['rnd', 'mv', 'df']:
    for selection_method in ['all', 'best']:
        fn = df_type.upper() + '_' + selection_method.upper() + '_'
        DATA_FUSION_FOLDERS[fn + 'CHF_2017'] = _full_path_to(fn + 'CHF_2017', 'rl')
        for mirex_submission_name in MIREX_SUBMISSION_NAMES:
            DATA_FUSION_FOLDERS[fn + mirex_submission_name] = _full_path_to(fn + mirex_submission_name, 'rl')

RESULT_TABLES = _full_path_to('', 'rt')
RESULT_FIGURES = _full_path_to('', 'rf')
RESULT_VISUALISATIONS = _full_path_to('', 'rv')


def init_folders():
    """
    Check if all folders that we need, exist. If they do not exist yet, create them.
    """
    needed_folders = [SYNTHMIDI_FOLDER, ALIGNMENTS_FOLDER, AUDIO_FEATURES_FOLDER, CHORDS_FROM_TABS_FOLDER,
                      MIDILABS_FOLDERS['bar'], MIDILABS_FOLDERS['beat'], TABLABS_FOLDER,
                      MIDILABS_CHORD_PROBABILITY_FOLDER, LOG_LIKELIHOOD_FOLDER, MIDILABS_ALIGNMENT_SCORE_FOLDER,
                      RESULT_TABLES, RESULT_FIGURES, RESULT_VISUALISATIONS]
    for folder_name in DATA_FUSION_FOLDERS:
        needed_folders.append(DATA_FUSION_FOLDERS[folder_name])
    for needed_folder in needed_folders:
        if not path.isdir(needed_folder):
            makedirs(needed_folder)


def get_all_songs():
    """
    Creates a dictionary of Song objects, indexed by integer keys. Key, title, album, ground truth chord labels,
    audio path and Chordify labels path are added to each song.

    :return: Dictionary of Songs in our data set.
    """
    # Import all songs, assign full paths
    all_songs = dict()
    with open(INDEX_PATH, 'r') as index_csv:
        index_csv_reader = csv.reader(index_csv, delimiter=';')
        for key_data_row in index_csv_reader:
            if len(key_data_row) >= 4:
                # This is a data row containing song information: key, title, album and path to ground truth label file
                key = int(key_data_row[0])  # NB: this is not the musical key, but an index
                title = key_data_row[1]
                album = key_data_row[2]
                full_chord_labs_path = get_full_chord_labs_path(key_data_row[3])
                full_segmentation_labs_path = get_full_segmentation_labs_path(key_data_row[3])
                all_songs[key] = Song(key, title, album, full_chord_labs_path, get_full_audio_path(key),
                                      full_segmentation_labs_path)

    # Find corresponding tabs
    with open(TAB_INDEX_PATH, 'r') as tab_index_csv:
        tab_index_csv_reader = csv.reader(tab_index_csv, delimiter=';')
        for tab_data_row in tab_index_csv_reader:
            if len(tab_data_row) >= 4:
                # This is a data row containing tab link information.
                key = int(tab_data_row[2])
                if key in all_songs:
                    # This tab file was manually matched to one of the songs in our data set.
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
        # MIREX
        for mirex_submission_name_str in MIREX_SUBMISSION_NAMES:
            all_songs[song_key].full_mirex_chord_lab_paths[mirex_submission_name_str] = \
                get_full_mirex_chord_labs_path(all_songs[song_key], mirex_submission_name_str)
    return all_songs


def _get_midi_chord_probability_path(segmentation_method: str, midi_name: str) -> str:
    """
    Get path of text file to read/write this MIDI chord probability from/to.

    :param segmentation_method: Bar or beat segmentation
    :param midi_name: Name of the MIDI file
    :return: Path of text file to read/write this MIDI chord probability from/to
    """
    return path.join(MIDILABS_CHORD_PROBABILITY_FOLDER, segmentation_method + '_' + midi_name + '.txt')


def write_midi_chord_probability(segmentation_method: str, midi_name: str, midi_chord_probability: float):
    """
    Write MIDI chord probability of this MIDI file to the corresponding text file

    :param segmentation_method: Bar or beat segmentation
    :param midi_name: Name of the MIDI file
    :param midi_chord_probability: Chord probability float
    """
    write_path = _get_midi_chord_probability_path(segmentation_method, midi_name)
    with open(write_path, 'w') as write_file:
        write_file.write(str(midi_chord_probability))


def read_midi_chord_probability(segmentation_method: str, midi_name: str) -> float:
    """
    Read MIDI chord probability of this MIDI file from the corresponding text file

    :param segmentation_method: Bar or beat segmentation
    :param midi_name: Name of the MIDI file
    :return: Chord probability float
    """
    read_path = _get_midi_chord_probability_path(segmentation_method, midi_name)
    with open(read_path, 'r') as reading_file:
        result = float(reading_file.read().rstrip())
    return result


def _get_midi_alignment_score_path(midi_name: str) -> str:
    """
    Get path of text file to read/write this MIDI alignment score from/to.

    :param midi_name: Name of MIDI file
    :return: Path of text file to read/write this MIDI alignment score from/to
    """
    return path.join(MIDILABS_ALIGNMENT_SCORE_FOLDER, midi_name + '.txt')


def write_chord_alignment_score(midi_name: str, alignment_score: float):
    """
    Write MIDI alignment score of this MIDI file to the corresponding file

    :param midi_name: Name of MIDI file
    :param alignment_score: MIDI alignment score
    """
    write_path = _get_midi_alignment_score_path(midi_name)
    with open(write_path, 'w') as write_file:
        write_file.write(str(alignment_score))


def read_chord_alignment_score(midi_name: str) -> float:
    """
    Read MIDI alignment score of this MIDI from the corresponding file

    :param midi_name: Name of MIDI file
    :return: MIDI alingment score float
    """
    read_path = _get_midi_alignment_score_path(midi_name)
    with open(read_path, 'r') as reading_file:
        result = float(reading_file.read().rstrip())
    return result


def _get_log_likelihood_path(song_key: int, tab_file_path: str):
    """
    Get path of text file to read/write this tab log-likelihood from/to

    :param song_key: Key of Song
    :param tab_file_path: Path to tab file
    :return: Path of text file to read/write this tab log-likelihood from/to
    """
    return path.join(LOG_LIKELIHOOD_FOLDER, str(song_key) + '_' + get_file_name_from_full_path(tab_file_path) + '.txt')


def write_log_likelihood(song_key: int, tab_file_path: str, log_likelihood: float, transposition: int):
    """
    Write tab log-likelihood of this tab file to the corresponding text file

    :param song_key: Key of Song
    :param tab_file_path: Path to tab file
    :param log_likelihood: Log-likelihood of this tab
    :param transposition: Transposition of this tab
    """
    write_path = _get_log_likelihood_path(song_key, tab_file_path)
    with open(write_path, 'w') as write_file:
        write_file.write(str(log_likelihood) + ';' + str(transposition))


def read_log_likelihood(song_key: int, tab_file_path: str) -> (float, str):
    """
    Read tab log-likelihood of this tab file from the corresponding text file

    :param song_key: Key of Song
    :param tab_file_path: Path to tab file
    :return: Log-likelihood float and transposition int of this tab
    """
    read_path = _get_log_likelihood_path(song_key, tab_file_path)
    with open(read_path, 'r') as reading_file:
        str_result = reading_file.read().rstrip().split(';')
    return float(str_result[0]), int(str_result[1])


def get_evaluation_table_path(method_name: str) -> str:
    """
    Get the full path to the csv file in which  this method is evaluated.

    :param method_name: Name of an ACE method
    :return: The full path to the csv file in which  this method is evaluated
    """
    return path.join(_full_path_to(method_name + '.csv', 'rt'))


def get_full_chord_labs_path(chord_labs_path: str) -> str:
    """
    Get the full path to the file in the ChordLabs folder

    :param chord_labs_path: not-full path to chord labs file
    :return: Full path to chord labs file
    """
    if chord_labs_path == '':
        return ''
    chord_labs_path_parts = chord_labs_path.split('\\')
    return path.join(CHORDLABS_FOLDER, chord_labs_path_parts[0], chord_labs_path_parts[1], chord_labs_path_parts[2])


def get_full_segmentation_labs_path(chord_labs_path: str) -> str:
    """
    Get the full path to the file in the SegmentationLabs folder

    :param chord_labs_path: not-full path to chord labs file
    :return: Full path to chord labs file
    """
    if chord_labs_path == '':
        return ''
    chord_labs_path_parts = chord_labs_path.split('\\')
    return path.join(SEGMENTATION_LABS_FOLDER, chord_labs_path_parts[0], chord_labs_path_parts[1],
                     chord_labs_path_parts[2])


def get_full_chordify_chord_labs_path(key: int) -> str:
    """
    Get the full path to the Chordify chord labels, given the key of a song

    :param key: The key of the song from which we need the Chordify chord labels
    :return: Full path to the Chordify chord labels of our song
    """
    return path.join(CHORDIFY_FOLDER, str(key) + '.txt')


def get_full_mirex_chord_labs_path(song: Song, mirex_submission_name_str: str) -> str:
    """
    Get the full path to the MIREX chord labels, given the Song and MIREX submission name

    :param song: Song for which we want to find the MIREX chord labels
    :param mirex_submission_name_str: Name of MIREX submission
    :return: Full path to the MIREX chord labels, given the Song and MIREX submission name
    """
    if mirex_submission_name_str == 'CHF_2017':  # Chordify
        return get_full_chordify_chord_labs_path(song.key)
    for name, labs_path in zip(MIREX_SUBMISSION_NAMES, MIREX_SUBMISSION_FOLDERS):
        if mirex_submission_name_str == name:
            return path.join(labs_path, path.relpath(song.full_ground_truth_chord_labs_path, CHORDLABS_FOLDER))
    raise Exception('Chord label file for this MIREX name was not found')


def get_full_midi_chord_labs_path(midi_file_name: str, segmentation_type: str) -> str:
    """
    Get the full path to the MIDI chord labels, given the midi file name

    :param midi_file_name: File name (not a full path!) to our MIDI file
    :param segmentation_type: Either 'bar' or 'beat'
    :return: Full path to the MIDI chord labels of our MIDI
    """
    return path.join(MIDILABS_FOLDERS[segmentation_type], midi_file_name + '.lab')


def get_full_tab_chord_labs_path(full_tab_file_path: str) -> str:
    """
    Get the full path to the tab chord labels, given the full path to the tab file

    :param full_tab_file_path: Tab file
    :return: Full path to the tab chord labels of our song
    """
    filename = get_file_name_from_full_path(full_tab_file_path)
    return path.join(TABLABS_FOLDER, filename + '.txt')


def get_full_audio_path(key: int) -> str:
    """
    Get the full path to the .wav file, given the key of a song

    :param key: The key of the song from which we need the audio
    :return: Full path to the audio of our song
    """
    return path.join(AUDIO_FOLDER, str(key) + '.wav')


def get_full_synthesized_midi_path(midi_file_name: str) -> str:
    """
    Get the full path to the .wav file that is a synthesized version of the MIDI specified by midi_file_name

    :param midi_file_name: File name (not a full path!) to our MIDI file
    :return: Full path to the .wav file that is a synthesized version of our MIDI
    """
    return path.join(SYNTHMIDI_FOLDER, midi_file_name + '.wav')


def get_full_midi_path(midi_file_name: str) -> str:
    """
    Get the full path to the .mid file of the MIDI specified by midi_file_name

    :param midi_file_name: File name (not a full path!) to our MIDI file
    :return: Full path to the .mid file of our MIDI
    """
    return path.join(MIDI_FOLDER, midi_file_name + '.mid')


def get_full_alignment_path(midi_file_name: str) -> str:
    """
    Get the full path to the .txt file of the alignment between our MIDI and the audio file it is matched to

    :param midi_file_name: File name (not a full path!) to our MIDI file
    :return: Full path to the .txt file that represents the alignment
    """
    return path.join(ALIGNMENTS_FOLDER, midi_file_name + '.txt')


def _get_midi_path_list() -> [str]:
    """
    Get a list with all .mid files in our MIDI folder
    :return: The list with all .mid files in our MIDI folder
    """
    result = []
    for midi_file in listdir(MIDI_FOLDER):
        if midi_file.endswith(".mid"):
            result.append(midi_file)
    return result


def get_relative_path(full_path: str) -> str:
    """
    Extract the relative path from the data folder

    :param full_path: The full path
    :return: Relative path from data folder

    >>> get_relative_path(path.join(DATA_PATH, 'MIDI/001-001.mid'))
    'MIDI/001-001.mid'
    """
    return path.relpath(full_path, DATA_PATH)


def get_absolute_path(relative_path: str) -> str:
    """
    Extract the absolute path from the data folder

    :param relative_path: Relative path from data folder
    :return: The full path

    >>> get_absolute_path('MIDI/001-001.mid').startswith(DATA_PATH)
    True
    """
    return path.join(DATA_PATH, relative_path)


def get_file_name_from_full_path(full_path: str) -> str:
    """
    Extract the file name (without extension) from a full path

    :param full_path: The full path we want to extract the file name from
    :return: The file name from our full path

    >>> get_file_name_from_full_path('/media/daphne/Seagate Expansion Drive/Data/MIDI/001-001.mid')
    '001-001'
    >>> get_file_name_from_full_path('/media/daphne/Seagate Expansion Drive/Data/MIDI/001-001.txt')
    '001-001'
    """
    return str(path.basename(full_path).split('.')[0])


def file_exists(full_path: str) -> bool:
    """
    Shortcut method to check if a file, specified by its full path exists

    :param full_path: Full path to the file of which we want to know if it exists
    :return: Does our file exist already?
    """
    return path.isfile(full_path)


def remove_file(remove_file_path: str):
    """
    Remove the file specified by remove_file_path

    :param remove_file_path: Path to the file which we will remove
    """
    remove(remove_file_path)


def get_chords_from_tab_filename(full_tab_file_path: str) -> str:
    """
    Get the filename to write the parsed chords from the tab file

    :param full_tab_file_path: Tab file
    :return: Filename for parsed chords
    """
    filename = get_file_name_from_full_path(full_tab_file_path)
    return path.join(CHORDS_FROM_TABS_FOLDER, filename + '.npy')


def get_full_audio_features_path(key: int) -> str:
    """
    Get the full path to the full audio features path of the song specified by the key

    :param key: Key of the song for which we need the audio features path
    :return: Audio features path of our song
    """
    return path.join(AUDIO_FEATURES_FOLDER, str(key) + '.npy')


def get_data_fusion_path(key: int, df_type_str: str, selection_method_str: str, audio_ace: str) -> str:
    """
    Get the full path to the data fusion labels path of the song specified by the key

    :param key: Key of the song for which we need the data fusion labels path
    :param df_type_str: Which type of data fusion; either 'rand', 'mv', 'df'
    :param selection_method_str: Do we use all labels or only the expected best?
    :param audio_ace: Which audio algorithm did we use (CHF or one of the MIREX algorithms)
    :return: Data fusion labels path of our song
    """
    return path.join(DATA_FUSION_FOLDERS[df_type_str.upper() + '_' + selection_method_str.upper() + '_' + audio_ace],
                     str(key) + '.lab')


def get_evaluation_table_by_audio_measure_path(audio_ace: str, measure: str) -> str:
    """
    Get the full path to the csv file in which this method is evaluated.

    :param audio_ace: Which audio algorithm did we use (CHF or one of the MIREX algorithms)
    :param measure: Which measure (e.g. CSR)
    :return: Data fusion labels path of our song
    """
    return path.join(_full_path_to(audio_ace + '-' + measure + '.csv', 'rt'))


def find_duplicate_midis(song: Song) -> [str]:
    """
    Duplicate MIDI's are MIDI's that yield exactly the same chord sequences on the beat level, but the files were not
    identified as identical based on MD5 checksum (typically due to some minor changes, like changing the MIDI title).

    :param song: Song in our data set
    :return: List of names of duplicate MIDI files
    """
    duplicate_midis = []
    all_labels = []
    for midi_path in song.full_midi_paths:
        midi_name = get_file_name_from_full_path(midi_path)
        midi_beat_lab_path = get_full_midi_chord_labs_path(midi_name, 'beat')
        with open(midi_beat_lab_path, 'r') as read_midi_beat_file:
            my_labels = read_midi_beat_file.readlines()
        if my_labels in all_labels:
            duplicate_midis.append(midi_name)
        else:
            all_labels.append(my_labels)
    return duplicate_midis


def read_alignment_file(file_path: str) -> ([float], [float]):
    """
    Read the alignment from a file

    :param file_path: Path to the alignment file
    :return: The alignment, read from a file
    """
    with open(file_path, 'r') as alignment_read_file:
        lines = alignment_read_file.readlines()
        p = []
        q = []
        for line in lines:
            line_parts = line.split()
            p.append(float(line_parts[1]))
            q.append(float(line_parts[2].rstrip()))
        return p, q


def get_well_aligned_midis(song: Song) -> [str]:
    """
    Return names of only the well-aligned MIDIs for this Song (excluding duplicates)

    :param song: Song in our data set
    """
    # Find duplicate MIDIs in this song; we will exclude them
    duplicate_midis = find_duplicate_midis(song)

    well_aligned_midis = []
    for full_midi_path in song.full_midi_paths:
        midi_name = get_file_name_from_full_path(full_midi_path)
        if midi_name not in duplicate_midis:
            alignment_score = read_chord_alignment_score(midi_name)
            if alignment_score <= 0.85:  # Properly aligned
                well_aligned_midis.append(midi_name)

    return well_aligned_midis


def get_expected_best_midi(song: Song) -> (str, str):
    """
    Find name of the expected best well-aligned MIDI and segmentation type for this Song
    (based on MIDI chord probability)

    :param song: Song in our data set
    """
    # We only consider well-aligned MIDIs
    well_aligned_midis = get_well_aligned_midis(song)

    # Return path to the best MIDI of the song
    best_midi_name, best_midi_quality, best_segmentation = '', -9999999999, ''
    for segmentation_type in 'bar', 'beat':
        for full_midi_path in well_aligned_midis:
            midi_name = get_file_name_from_full_path(full_midi_path)
            midi_chord_probability = read_midi_chord_probability(segmentation_type, midi_name)
            if midi_chord_probability > best_midi_quality:
                # This is the best MIDI & segmentation type we have seen until now
                best_midi_name, best_midi_quality, best_segmentation = \
                    midi_name, midi_chord_probability, segmentation_type

    return best_midi_name, best_segmentation


def get_expected_best_tab_lab(song: Song) -> str:
    """
    Find the lab file of the expected best tab for this Song (based on log-likelihood returned by Jump Alignment)

    :param song: Song in our data set
    """
    best_tab_lab, best_tab_quality = '', 0

    for tab_path in song.full_tab_paths:
        tab_write_path = get_full_tab_chord_labs_path(tab_path)
        if file_exists(tab_write_path):
            tab_quality, _ = read_log_likelihood(song.key, tab_path)
            if tab_quality > best_tab_quality:
                best_tab_lab, best_tab_quality = tab_write_path, tab_quality

    return best_tab_lab


def get_lab_visualisation_path(song: Song, audio_ace: str) -> str:
    """
    Find the location of the png of the lab visualisation path for a given song and audio ace method.
    :param song: Song for which we need the lab visualisation path
    :param audio_ace: Audio method for which we need the lab visualisation path
    :return: The location of the png of the lab visualisation path for a given song and audio ace method.
    """
    return path.join(RESULT_VISUALISATIONS, str(song.key) + '_' + audio_ace + '.png')
