from typing import List

from decibel.midi_chord_recognizer.midi_segmenter_interface import MIDISegmenterInterface
from decibel.audio_midi_aligner.realigned_midi import RealignedMIDI


class MIDINoteSegmenter(MIDISegmenterInterface):
    def __init__(self):
        super().__init__()
        self.segmenter_name = 'note'

    def _get_partition_points(self, realigned_midi: RealignedMIDI) -> List[float]:
        """
        Find all points in the MIDI file where a note starts or ends

        :return: Partition points on note level
        """
        partition_points = [0]
        for instrument in realigned_midi.midi_data.instruments:
            if not instrument.is_drum:
                for note in instrument.notes:
                    if note.start not in partition_points:
                        partition_points.append(note.start)
                    if note.end not in partition_points:
                        partition_points.append(note.end)
        return sorted(partition_points)
