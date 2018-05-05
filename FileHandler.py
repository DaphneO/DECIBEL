# -*- coding: utf-8 -*-
from os import path, listdir
from sys import platform
import csv
from Song import Song

# Find DATA_PATH
if platform == 'linux2':  # Lubuntu laptop
    DATA_PATH = "/media/daphne/Seagate Expansion Drive/Data"
else:  # Windows laptop
    DATA_PATH = "E:\Data"

MIDI_FOLDER = path.join(DATA_PATH, 'MIDI')
AUDIO_FOLDER = path.join(DATA_PATH, 'Audio', 'Wavs')
CHORDIFY_FOLDER = path.join(DATA_PATH, 'chordify_output')
CHORDLABS_FOLDER = path.join(DATA_PATH, 'ChordLabs')
MIDILABS_FOLDER = path.join(DATA_PATH, 'MIDIlabs')
SYNTHMIDI_FOLDER = path.join(DATA_PATH, 'SynthMIDI')
TABS_FOLDER = path.join(DATA_PATH, 'Tabs')
ALIGNMENTS_FOLDER = path.join(DATA_PATH, 'Alignments')

INDEX_PATH = path.join(DATA_PATH, 'IndexAudio.csv')
TAB_INDEX_PATH = path.join(DATA_PATH, 'IndexTabs.csv')

SOUND_FONT_PATH = '/usr/share/sounds/sf2/FluidR3_GM.sf2'

MIDILABS_RESULTS_PATH = path.join(DATA_PATH, 'MidiLabsResults.csv')
MIDILABS_CHORD_PROBABILITY_PATH = path.join(DATA_PATH, 'MidiLabsChordProbabilities.csv')


def get_all_songs():
    # Import all songs, assign full paths
    all_songs = dict()
    with open(INDEX_PATH, 'rb') as index_csv:
        index_csv_reader = csv.reader(index_csv, delimiter=';')
        for key_data_row in index_csv_reader:
            if len(key_data_row) >= 4:
                key = int(key_data_row[0])
                title = key_data_row[1]
                album = key_data_row[2]
                chord_labs_path = key_data_row[3]
                all_songs[key] = Song(key, title, album, chord_labs_path)
    # Find corresponding tabs
    with open(TAB_INDEX_PATH, 'r') as tab_index_csv:
        tab_index_csv_reader = csv.reader(tab_index_csv, delimiter=';')
        for tab_data_row in tab_index_csv_reader:
            if len(tab_data_row) >= 4:
                key = int(tab_data_row[2])
                tab_path = tab_data_row[3]
                all_songs[key].add_tab_path(tab_path)
    # Find corresponding MIDIs
    all_midis = get_midi_path_list()
    for midi_file_name in all_midis:
        midi_key = int(midi_file_name.split('-')[0])
        all_songs[midi_key].add_midi_path(midi_file_name)
    return all_songs


def get_full_chord_labs_path(chord_labs_path):
    if chord_labs_path == '':
        return ''
    chord_labs_path_parts = chord_labs_path.split('\\')
    return path.join(CHORDLABS_FOLDER, chord_labs_path_parts[0], chord_labs_path_parts[1])


def get_full_audio_path(key_str):
    return path.join(AUDIO_FOLDER, str(key_str) + '.wav')


def get_full_tab_path(tab_path):
    return path.join(TABS_FOLDER, tab_path)


def get_full_midi_path(midi_path):
    return path.join(MIDI_FOLDER, midi_path)


def get_full_synthesized_midi_path(synthesized_midi_path):
    return path.join(SYNTHMIDI_FOLDER, synthesized_midi_path)


def get_midi_path_list():
    result = []
    for midi_file in listdir(MIDI_FOLDER):
        if midi_file.endswith(".mid"):
            result.append(midi_file)
    return result


def get_file_name_from_full_path(full_path):
    return path.basename(full_path).split('.')[0]
