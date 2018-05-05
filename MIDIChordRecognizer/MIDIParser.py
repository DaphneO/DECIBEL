# -*- coding: utf-8 -*-
import pretty_midi
from Chords import *
import FileHandler
from os import path


class Event:
    def __init__(self, start_time, end_time, all_chords_list):
        self.all_chords_list = all_chords_list
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.notes = []
        self.pitches = set()
        self.pitch_classes = set()
        self.chroma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.most_likely_chord = None
        self.most_likely_chord_score = -10

    def add_note(self, note):
        assert isinstance(note, pretty_midi.Note)
        self.notes.append(note)
        self.pitches.add(Pitch(note.pitch))
        pitch_class_nr = note.pitch % 12
        self.pitch_classes.add(PitchClass(pitch_class_nr))
        self.chroma[pitch_class_nr] += (self.note_duration_ratio_in_event(note) * note.velocity)

    def __hash__(self):
        return hash(self.start_time)

    def note_duration_ratio_in_event(self, note):
        start_inside_event = max(self.start_time, note.start)
        end_inside_event = min(self.end_time, note.end)
        duration_inside_event = end_inside_event - start_inside_event
        return duration_inside_event / self.duration

    def normalize(self):
        s = sum(self.chroma)
        if s > 0:
            self.chroma = [i / s for i in self.chroma]

    def find_most_likely_chord(self):
        best_matching_chord_score = -2.99
        best_matching_chord_str = 'X'
        best_key_note_weight = 0
        for [key_note, chord_type, chord_template] in self.all_chords_list:
            chord_score = self._score_compared_to_template(chord_template)
            if chord_score > best_matching_chord_score or \
                (chord_score == best_matching_chord_score and self.chroma[key_note] > best_key_note_weight):
                best_matching_chord_score = chord_score
                best_matching_chord_str = PITCH_CLASSES[key_note] + chord_type
                best_key_note_weight = self.chroma[key_note]
        if best_matching_chord_str == 'X':
            self.most_likely_chord = None
            self.most_likely_chord_score = best_matching_chord_score
        else:
            self.most_likely_chord = Chord.from_common_tab_notation_string(best_matching_chord_str)
            self.most_likely_chord_score = best_matching_chord_score

    def _score_compared_to_template(self, template):
        if sum(self.chroma) > 0:
            interesting = True
        p = 0
        n = 0
        # Iterate over chroma elements, sum matching and missing weights
        for i in range(12):
            if self.chroma[i] > 0:
                # This note is in the chroma. Let's see if it is in the template
                if template[i] == 1:
                    p += self.chroma[i]
                else:
                    n += self.chroma[i]
        m = 0
        # Count the number of unmatched template elements
        for i in range(12):
            if template[i] == 1 and self.chroma[i] == 0:
                m += 1
        return p - n - m  # Higher scores means higher similarity, so a better matching template!

    def __str__(self):
        return str(self.start_time)[:5] + '-' + str(self.end_time)[:5] + ':' + str(self.most_likely_chord)


class MIDI:
    def __init__(self, midi_path, alignment, all_chords_list, partition_method='bar'):
        self.all_chords_list = all_chords_list
        self.midi_data = pretty_midi.PrettyMIDI(midi_path)
        self.midi_data.adjust_times(alignment[0], alignment[1])
        self.midi_data.remove_invalid_notes()
        self.events = dict()
        self.find_events(partition_method)

    def find_events(self, partition_method):
        # Find all partition points
        if partition_method == 'note':
            partition_points = self._partition_by_note_events()
        elif partition_method == 'beat':
            partition_points = self._partition_by_beats()
        else:
            partition_points = self._partition_by_bars()

        # Create events
        for i in range(0, len(partition_points) - 1):
            self.events[partition_points[i]] = Event(partition_points[i], partition_points[i + 1], self.all_chords_list)

        # Add each note to the corresponding events
        for instrument in self.midi_data.instruments:
            if not instrument.is_drum:
                # We assert that instrument.notes are ordered on start value for each instrument
                start_index = 0
                for note in instrument.notes:
                    # Find suitable start_index
                    while start_index < len(partition_points) - 1 \
                            and note.start >= self.events[partition_points[start_index]].end_time:
                        start_index += 1
                    # Add this note to each event during which it sounds
                    last_index = start_index
                    self.events[partition_points[last_index]].add_note(note)
                    while last_index < len(partition_points) - 1 \
                            and note.end > self.events[partition_points[last_index]].end_time:
                        last_index += 1
                        self.events[partition_points[last_index]].add_note(note)

        # Normalize each event
        for event_key in self.events:
            self.events[event_key].normalize()

        # Find most likely chord
        for event_key in self.events:
            self.events[event_key].find_most_likely_chord()

    def concatenate_events(self):
        new_events = dict()
        current_event = self.events[0]
        last_added = False
        sorted_keys = sorted(self.events)
        for event_key in sorted_keys:
            if self.events[event_key].most_likely_chord == current_event.most_likely_chord:
                current_event.end_time = self.events[event_key].end_time
                last_added = False
            else:
                new_events[current_event.start_time] = current_event
                current_event = self.events[event_key]
                last_added = True
        if not last_added:
            new_events[current_event.start_time] = current_event

        self.events = new_events

    def export_chords(self, midi_name, path_string, chord_probability_write_object):
        chord_probability_count = 0
        chord_probability_sum = 0.0
        with open(path_string, 'w') as write_file:
            sorted_events = sorted(self.events)
            for event_key in sorted_events:
                event = self.events[event_key]
                chord_string = str(event.most_likely_chord)
                if chord_string == 'None':
                    chord_string = 'N'
                write_file.write(str(event.start_time) + ' ' + str(event.end_time) + ' ' +
                                 chord_string + '\n')
                chord_probability_count += 1
                chord_probability_sum += event.most_likely_chord_score
        chord_probability_write_object.write(
            '{0} {1}\n'.format(midi_name, str(chord_probability_sum / chord_probability_count)))

    def _partition_by_note_events(self):
        partition_points = [0]
        for instrument in self.midi_data.instruments:
            if not instrument.is_drum:
                for note in instrument.notes:
                    if note.start not in partition_points:
                        partition_points.append(note.start)
                    if note.end not in partition_points:
                        partition_points.append(note.end)
        return sorted(partition_points)

    def _partition_by_beats(self):
        beats = list(self.midi_data.get_beats())
        # Extrapolate one ending beat
        beats.append(beats[-1] + (beats[-1] - beats[-2]))
        return beats

    def _partition_by_bars(self):
        bars = list(self.midi_data.get_downbeats())
        # Extrapolate one ending bar
        bars.append(bars[-1] + (bars[-1] - bars[-2]))
        return bars


def classify_all_aligned_midis(all_songs, all_chords_list):
    with open(FileHandler.MIDILABS_CHORD_PROBABILITY_PATH, 'a') as chord_probability_write_file:
        for song_key in all_songs:
            song = all_songs[song_key]
            for alignment in song.midi_alignments:
                synthesized_midi_path = alignment.midi
                midi_name = FileHandler.get_file_name_from_full_path(synthesized_midi_path)
                midi_path = path.join(FileHandler.MIDI_FOLDER, midi_name + '.mid')
                write_path = path.join(FileHandler.MIDILABS_FOLDER, midi_name + '.lab')
                if not path.isfile(write_path):
                    try:
                        aligned_midi = MIDI(midi_path, alignment.alignment_path, all_chords_list, 'bar')
                        aligned_midi.concatenate_events()
                        aligned_midi.export_chords(midi_name, write_path, chord_probability_write_file)
                        song.midi_labs.append(write_path)
                    except:
                        print(midi_name + " went wrong")
                else:
                    song.midi_labs.append(write_path)
