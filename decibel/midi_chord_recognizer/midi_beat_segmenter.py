from typing import List

from decibel.midi_chord_recognizer.midi_segmenter_interface import MIDISegmenterInterface
from decibel.audio_midi_aligner.realigned_midi import RealignedMIDI


class MIDIBeatSegmenter(MIDISegmenterInterface):
    def __init__(self):
        super().__init__()
        self.segmenter_name = 'beat'

    def _get_partition_points(self, realigned_midi: RealignedMIDI) -> List[float]:
        """
        Find all points in the MIDI file where a new beat starts

        :return: Partition points on beat level
        """
        beats = list(realigned_midi.midi_data.get_beats())
        # Extrapolate one ending beat
        beats.append(beats[-1] + (beats[-1] - beats[-2]))
        return beats
