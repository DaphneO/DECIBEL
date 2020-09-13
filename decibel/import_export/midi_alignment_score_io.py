from os import path

from decibel.audio_midi_aligner.alignment_score import AlignmentScore
from decibel.import_export.filehandler import MIDILABS_ALIGNMENT_SCORE_FOLDER


def read_chord_alignment_score(midi_name: str) -> AlignmentScore:
    """
    Read MIDI alignment score of this MIDI from the corresponding file

    :param midi_name: Name of MIDI file
    :return: MIDI alignment score
    """
    read_path = _get_midi_alignment_score_path(midi_name)
    with open(read_path, 'r') as reading_file:
        result = AlignmentScore(reading_file.read().rstrip())
    return result


def _get_midi_alignment_score_path(midi_name: str) -> str:
    """
    Get path of text file to read/write this MIDI alignment score from/to.

    :param midi_name: Name of MIDI file
    :return: Path of text file to read/write this MIDI alignment score from/to
    """
    return path.join(MIDILABS_ALIGNMENT_SCORE_FOLDER, midi_name + '.txt')


def write_chord_alignment_score(midi_name: str, alignment_score: float):
    """
    Write MIDI alignment score of this MIDI file to the corresponding file

    :param midi_name: Name of MIDI file
    :param alignment_score: MIDI alignment score
    """
    write_path = _get_midi_alignment_score_path(midi_name)
    with open(write_path, 'w') as write_file:
        write_file.write(str(alignment_score))
