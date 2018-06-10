# -*- coding: utf-8 -*-
import librosa


class Song:
    def __init__(self, key, title, album, full_ground_truth_chord_labs_path, full_audio_path):
        # type: (int, str, str, str) -> None
        """
        Create a new song. All information we extract from any representation of this song, is added to the Song object
        :param key: Integer key of this song - we use this for matching all representations of the song
        :param title: Title of the song
        :param album: Album on which the song appears
        :param ground_truth_chord_labs_path:
        """
        # Key, title, album and ground truth chord_labs_path are known from the beginning
        self.key = key
        self.title = title
        self.album = album
        self.full_ground_truth_chord_labs_path = full_ground_truth_chord_labs_path
        self.full_audio_path = full_audio_path
        self.duration = librosa.get_duration(filename=self.full_audio_path)

        # Tab paths, midi paths and ground truth chord labels are filled by get_all_songs
        self.full_midi_paths = []
        self.full_tab_paths = []
        self.chord_labs = []  # todo: Check if this is really used
        self.full_chordify_chord_labs_path = ''

        self.full_synthesized_midi_paths = []
        self.midi_alignments = []
        self.midi_labs = []
        self.audio_features_path = ''

        self.results = []

    def add_midi_path(self, full_midi_path):
        self.full_midi_paths.append(full_midi_path)

    def add_tab_path(self, full_tab_path):
        self.full_tab_paths.append(full_tab_path)
