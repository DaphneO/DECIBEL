from typing import Tuple

import pretty_midi

from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_annotation_item import ChordAnnotationItem
from decibel.music_objects.chord_template import ChordTemplate
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.pitch import Pitch
from decibel.music_objects.pitch_class import PitchClass


class Event:
    def __init__(self, start_time: float, end_time: float):
        """
        Create a new event

        :param start_time: Start time of the event, in seconds
        :param end_time: End time of the event, in seconds
        """
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.notes = []
        self.pitches = set()
        self.pitch_classes = set()
        self.chroma = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __hash__(self):
        """
        Hash the event to an integer (based on its unique start time), so we can use it as a key in a dictionary

        :return: Integer that uniquely determines this event
        """
        return hash(self.start_time)

    def __str__(self):
        """
        Returns an easily readable string representation of the Event

        :return: Easily readable string representation of the Event
        """
        return str(self.start_time)[:5] + '-' + str(self.end_time)[:5]

    def add_note(self, note: pretty_midi.Note):
        """
        Add a Note to the Event

        :param note: The Note we add to the Event
        """
        self.notes.append(note)
        self.pitches.add(Pitch(note.pitch))
        pitch_class_nr = note.pitch % 12
        self.pitch_classes.add(PitchClass(pitch_class_nr))
        self.chroma[pitch_class_nr] += (self._note_duration_ratio_in_event(note) * note.velocity)

    def _note_duration_ratio_in_event(self, note: pretty_midi.Note):
        """
        Calculate the ratio of the event during which this note sounds

        :param note: Note for which we want to know the duration ratio
        :return: Duration ratio of this note in the event.
        """
        start_inside_event = max(self.start_time, note.start)
        end_inside_event = min(self.end_time, note.end)
        duration_inside_event = end_inside_event - start_inside_event
        return duration_inside_event / self.duration

    def normalize(self):
        """
        Normalize the chroma feature of the event.
        """
        s = sum(self.chroma)
        if s > 0:
            self.chroma = [i / s for i in self.chroma]

    def find_most_likely_chord(self, chord_vocabulary: ChordVocabulary) -> Tuple[ChordAnnotationItem, float]:
        """
        Find the chord to which the chroma of this event matches best.

        :param chord_vocabulary: List of all chords for classification
        """
        best_matching_chord_score = -2.99
        best_matching_chord_str = 'X'
        best_key_note_weight = 0
        for chord_template in chord_vocabulary.chord_templates:
            chord_score = self._score_compared_to_template(chord_template)
            if chord_score > best_matching_chord_score or (chord_score == best_matching_chord_score and
                                                           self.chroma[chord_template.key] > best_key_note_weight):
                best_matching_chord_score = chord_score
                best_matching_chord_str = str(PitchClass(chord_template.key)) + chord_template.mode
                best_key_note_weight = self.chroma[chord_template.key]
        if best_matching_chord_str == 'X':
            most_likely_chord = None
        else:
            most_likely_chord = Chord.from_common_tab_notation_string(best_matching_chord_str)
        return ChordAnnotationItem(self.start_time, self.end_time, most_likely_chord), best_matching_chord_score

    def _score_compared_to_template(self, chord_template: ChordTemplate):
        """
        Calculate the score of the chroma of this Event compared to the specified chord template

        :param chord_template: The chord template we compare to
        :return: Similarity score
        """
        p = 0
        n = 0
        # Iterate over chroma elements, sum matching and missing weights
        for i in range(12):
            if self.chroma[i] > 0:
                # This note is in the chroma. Let's see if it is in the chord_template
                if chord_template.chroma_list[i] == 1:
                    p += self.chroma[i]
                else:
                    n += self.chroma[i]
        m = 0
        # Count the number of unmatched chord_template elements
        for i in range(12):
            if chord_template.chroma_list[i] == 1 and self.chroma[i] == 0:
                m += 1
        return p - n - m  # Higher scores means higher similarity, so a better matching chord_template!
