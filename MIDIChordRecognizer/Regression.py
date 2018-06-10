import random
from sklearn.linear_model import LinearRegression
import numpy as np

midi_labs_chord_probabilities_path = '/media/daphne/Seagate Expansion Drive/Data/MidiLabsChordProbabilities.csv'
midi_labs_results_path = '/media/daphne/Seagate Expansion Drive/Data/MidiLabsResults.csv'

midi_results = dict()

with open(midi_labs_results_path, 'r') as read_results:
    for line in read_results:
        midi_key, alignment_error, root, min_maj, sevenths = line.rstrip().split(';')[0:5]
        song_key = int(midi_key[0:3])
        alignment_error = float(alignment_error)
        root = float(root)
        min_maj = float(min_maj)
        sevenths = float(sevenths)
        if not midi_results.has_key(song_key):
            midi_results[song_key] = []
        midi_results[song_key].append([midi_key, alignment_error, root, min_maj, sevenths])

with open(midi_labs_chord_probabilities_path, 'r') as read_chordprobs:
    for line in read_chordprobs:
        midi_key, chord_probability = line.rstrip().split(' ' )[0:2]
        song_key = int(midi_key[0:3])
        chord_probability = float(chord_probability)
        for item_list in midi_results[song_key]:
            if item_list[0] == midi_key:
                item_list.append(chord_probability)

all_song_keys = midi_results.keys()

training_song_keys = random.sample(all_song_keys, 100)

training_alignment_error = []
training_chord_probability = []
training_root = []
training_min_maj = []
training_sevenths = []

for training_song_key in training_song_keys:
    for midi_list in midi_results[training_song_key]:
        training_alignment_error.append(midi_list[1])
        training_chord_probability.append(midi_list[5])
        training_root.append(midi_list[2])
        training_min_maj.append(midi_list[3])
        training_sevenths.append(midi_list[4])

training_alignment_error = np.array(training_alignment_error)
training_chord_probability = np.array(training_chord_probability)
training_root = np.array(training_root)
training_min_maj = np.array(training_min_maj)
training_sevenths = np.array(training_sevenths)

training_full = np.c_[training_alignment_error, training_chord_probability, training_root, training_min_maj, training_sevenths]

lm = LinearRegression()
lm.fit(training_full[:, 0:2], training_full[:, 3])

stop = True
