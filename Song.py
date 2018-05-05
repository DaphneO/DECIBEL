# -*- coding: utf-8 -*-
import FileHandler


class Song:
    def __init__(self, key, title, album, chord_labs_path):
        self.key = key
        self.title = title
        self.album = album
        self.full_chord_labs_path = FileHandler.get_full_chord_labs_path(chord_labs_path)
        self.full_audio_path = FileHandler.get_full_audio_path(key)
        self.full_midi_paths = []
        self.full_synthesized_midi_paths = []
        self.full_tab_paths = []
        self.chord_labs = []
        self.midi_labs = []
        self.midi_alignments = []

    def add_midi_path(self, midi_path):
        self.full_midi_paths.append(FileHandler.get_full_midi_path(midi_path))

    def add_tab_path(self, tab_path):
        self.full_tab_paths.append(FileHandler.get_full_tab_path(tab_path))
