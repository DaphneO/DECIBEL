from typing import List

from decibel.music_objects.chord_annotation_item import ChordAnnotationItem


class ChordAnnotation:
    def __init__(self):
        self.chord_annotation_items: List[ChordAnnotationItem] = []

    def add_chord_annotation_item(self, chord_annotation_item: ChordAnnotationItem):
        self.chord_annotation_items.append(chord_annotation_item)
