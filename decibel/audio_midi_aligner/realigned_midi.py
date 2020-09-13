import pretty_midi

import decibel.import_export.midi_alignment_io
from decibel.import_export import filehandler


class RealignedMIDI:
    def __init__(self, midi_path: str, alignment_path: str):
        """
        Create MIDI object, which represents the realigned pretty_midi using the specified alignment

        :param midi_path: Full path to the .mid file
        :param alignment_path: Alignment path
        """
        # Load pretty_midi object
        self.midi_data = pretty_midi.PrettyMIDI(midi_path)
        # Adjust the timing of the pretty_midi object, using the alignment path
        self.alignment = decibel.import_export.midi_alignment_io.read_alignment_file(alignment_path)
        self.midi_data.adjust_times(self.alignment.original_times, self.alignment.new_times)
        # Remove any notes whose end time is before or at their start time
        self.midi_data.remove_invalid_notes()
