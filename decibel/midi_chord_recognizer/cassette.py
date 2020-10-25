"""
CASSETTE (Chord estimation Applied to Symbolic music by Segmentation, Extraction and Tie-breaking TEmplate matching) is
a chord_template-matching based algorithm for MIDI chord recognition that is easy to implement and understand. Similar
to the good old cassette tapes, this algorithm is certainly not state of the art. However, it is simple to implement
and does not require any training.

CASSETTE recognizes chords in a three-step procedure:

1. It segments each audio-aligned midi file (on bar/beat/note level);
2. It calculates a weighted chroma feature for each of the segments, based on the notes within that segment;
3. It matches the features of each segment to the features of a predefined chord vocabulary and assigns each segment to
   the most similar chord.

The main function to use is :py:func:`classify_aligned_midis_for_song`, which calls CASSETTE on all MIDIs matched to
the given Song.
"""

# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple

from decibel.import_export.chord_annotation_io import export_chord_annotation
from decibel.midi_chord_recognizer.event import Event
from decibel.midi_chord_recognizer.midi_segmenter_interface import MIDISegmenterInterface
from decibel.audio_midi_aligner.realigned_midi import RealignedMIDI
from decibel.music_objects.chord_annotation import ChordAnnotation
from decibel.music_objects.chord_annotation_item import ChordAnnotationItem
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from decibel.import_export import filehandler


def _assign_most_likely_chords(events: Dict[float, Event], chord_vocabulary: ChordVocabulary) -> \
        List[Tuple[ChordAnnotationItem, float]]:
    return [events[event_key].find_most_likely_chord(chord_vocabulary) for event_key in events.keys()]


def _get_midi_chord_annotation(scored_annotation_items: List[Tuple[ChordAnnotationItem, float]]) -> ChordAnnotation:
    midi_chord_annotation = ChordAnnotation()

    current_annotation, _ = scored_annotation_items[0]
    last_added = False
    for annotation_item, _ in scored_annotation_items:
        if annotation_item.chord == current_annotation.chord:
            current_annotation.to_time = annotation_item.to_time
            last_added = False
        else:
            midi_chord_annotation.add_chord_annotation_item(current_annotation)
            current_annotation = annotation_item
            last_added = True
    if not last_added:
        midi_chord_annotation.add_chord_annotation_item(current_annotation)

    return midi_chord_annotation


def _compute_midi_chord_probability(scored_annotation_items: List[Tuple[ChordAnnotationItem, float]]) -> float:
    chord_probability_count = 0
    chord_probability_sum = 0.0
    for annotation_item, annotation_chord_score in scored_annotation_items:
        chord_probability_count += 1  # TODO check: change into length?
        chord_probability_sum += annotation_chord_score
    return chord_probability_sum / chord_probability_count


def classify_aligned_midis_for_song(song: Song, chord_vocabulary: ChordVocabulary, segmenter: MIDISegmenterInterface):
    """
    Find chord labels for all re-aligned MIDIs of this song

    :param song: Song object for which we want to find the chord labels
    :param chord_vocabulary: List of all chords
    :param segmenter: Bar or beat segmenter
    """
    for full_midi_path in song.full_midi_paths:
        midi_name = filehandler.get_file_name_from_full_path(full_midi_path)
        full_alignment_path = filehandler.get_full_alignment_path(midi_name)
        write_path = filehandler.get_full_midi_chord_labs_path(midi_name, segmenter.segmenter_name)
        if not filehandler.file_exists(write_path):
            # The file does not exist yet, so we need to find the chords
            # try:
                # Realign the MIDI using the alignment path
            realigned_midi = RealignedMIDI(full_midi_path, full_alignment_path)
            # Find Events, using the specified partition method
            events = segmenter.find_events(realigned_midi)
            # Assign most likely chords to each event
            most_likely_chords = _assign_most_likely_chords(events, chord_vocabulary)
            # Compute average chord probability
            midi_chord_probability = _compute_midi_chord_probability(most_likely_chords)
            # Concatenate annotation items with the same chord labels into one annotation.
            concatenated_annotation = _get_midi_chord_annotation(most_likely_chords)
            # Export results
            export_chord_annotation(concatenated_annotation, write_path)
            filehandler.write_midi_chord_probability(segmenter.segmenter_name, midi_name, midi_chord_probability)
                # except:
                #     print(midi_name + " went wrong")
