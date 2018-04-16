# -*- coding: utf-8 -*-
from Chords import Chord


def add_harte_labels(all_songs):
    for song_key in all_songs:
        song = all_songs[song_key]
        file_result = []
        if song.full_chord_labs_path != '':
            with open(song.full_chord_labs_path, "r") as lab_file:
                content = lab_file.readlines()
            for line in content:
                elements = line.split()
                start_time = elements[0]
                end_time = elements[1]
                chord = Chord.from_harte_chord_string(elements[2].replace('\n', ''))
                file_result.append((start_time, end_time, chord))
        all_songs[song.key].chord_labs = file_result
