import numpy as np

from decibel.audio_midi_aligner.midi_alignment import MIDIAlignment


def read_alignment_file(file_path: str) -> MIDIAlignment:
    """
    Read the alignment from a file

    :param file_path: Path to the alignment file
    :return: The alignment, read from a file
    """
    alignment_array = np.loadtxt(file_path)
    return MIDIAlignment(alignment_array[:, 1], alignment_array[:, 2])


def write_alignment_file(midi_alignment: MIDIAlignment, file_path: str):
    array = np.concatenate((np.array(range(len(midi_alignment.original_times))).reshape(-1, 1),
                            midi_alignment.original_times.reshape(-1, 1),
                            midi_alignment.new_times.reshape(-1, 1)), axis=1)
    np.savetxt(file_path, array)
