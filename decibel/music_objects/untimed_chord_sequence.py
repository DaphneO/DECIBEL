from typing import List

from decibel.music_objects.untimed_chord_sequence_item import UntimedChordSequenceItem


class UntimedChordSequence:
    def __init__(self):
        self.untimed_chord_sequence_item_items: List[UntimedChordSequenceItem] = []

    def add_untimed_chord_sequence_item(self, untimed_chord_sequence_item: UntimedChordSequenceItem):
        self.untimed_chord_sequence_item_items.append(untimed_chord_sequence_item)
