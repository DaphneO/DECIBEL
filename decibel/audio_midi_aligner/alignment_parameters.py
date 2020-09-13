class AlignmentParameters:
    def __init__(self, sampling_rate: int = 22050, lowest_midi_note: int = 36, nr_of_midi_notes: int = 48,
                 hop_length: int = 1048, gully: float = 0.96):
        # CQT parameters
        self.sampling_rate = sampling_rate
        self.lowest_midi_note = lowest_midi_note
        self.nr_of_midi_notes = nr_of_midi_notes
        self.hop_length = hop_length
        # DTW parameters
        self.gully = gully
