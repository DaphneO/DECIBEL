from typing import List, Dict

from decibel.midi_chord_recognizer.event import Event
from decibel.audio_midi_aligner.realigned_midi import RealignedMIDI


class MIDISegmenterInterface:
    def __init__(self):
        self.segmenter_name = None

    def _get_partition_points(self, realigned_midi: RealignedMIDI) -> List[float]:
        pass

    def find_events(self, realigned_midi: RealignedMIDI) -> Dict[float, Event]:
        # Find all partition points
        partition_points = self._get_partition_points(realigned_midi)

        # Create events
        events = dict()
        for i in range(0, len(partition_points) - 1):
            events[partition_points[i]] = \
                Event(partition_points[i], partition_points[i + 1])

        # Add each note to the corresponding events
        for instrument in realigned_midi.midi_data.instruments:
            if not instrument.is_drum:
                # We assert that instrument.notes are ordered on start value for each instrument
                start_index = 0
                for note in instrument.notes:
                    # Find suitable start_index
                    while start_index < len(partition_points) - 1 \
                            and note.start >= events[partition_points[start_index]].end_time:
                        start_index += 1
                    # Add this note to each event during which it sounds
                    last_index = start_index
                    events[partition_points[last_index]].add_note(note)
                    while last_index < len(partition_points) - 1 \
                            and note.end > events[partition_points[last_index]].end_time:
                        last_index += 1
                        events[partition_points[last_index]].add_note(note)

        # Normalize each event
        for event_key in events:
            events[event_key].normalize()

        return events
