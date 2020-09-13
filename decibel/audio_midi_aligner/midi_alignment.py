import numpy as np


class MIDIAlignment:
    def __init__(self, original_times: np.ndarray, new_times: np.ndarray):
        self.original_times = original_times
        self.new_times = new_times
