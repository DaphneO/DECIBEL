from typing import List

from decibel.midi_chord_recognizer.midi_segmenter_interface import MIDISegmenterInterface
from decibel.audio_midi_aligner.realigned_midi import RealignedMIDI


class MIDIBarSegmenter(MIDISegmenterInterface):
    def __init__(self):
        super().__init__()
        self.segmenter_name = 'bar'

    def _get_partition_points(self, realigned_midi: RealignedMIDI) -> List[float]:
        """
        Find all points in the MIDI file where a new bar starts

        :return: Partition points on bar level
        """
        bars = list(realigned_midi.midi_data.get_downbeats())
        # Extrapolate one ending bar
        bars.append(bars[-1] + (bars[-1] - bars[-2]))
        return bars
