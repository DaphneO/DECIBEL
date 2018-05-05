import pretty_midi
import librosa
import PureAligner
import FileHandler
from os import path


def _get_realigned_midi_object(alignment):
    # type: (PureAligner.Alignment) -> pretty_midi.PrettyMIDI
    synthesized_midi_path = alignment.midi
    midi_name = FileHandler.get_file_name_from_full_path(synthesized_midi_path)
    midi_path = path.join(FileHandler.MIDI_FOLDER, midi_name + '.mid')
    midi_object = pretty_midi.PrettyMIDI(midi_path)
    midi_object.adjust_times(alignment.alignment_path[0], alignment.alignment_path[1])
    midi_object.remove_invalid_notes()
    return midi_object


def export_alignment_to_midi(alignment, write_path):
    # type: (PureAligner.Alignment, str) -> ()
    realigned_midi_object = _get_realigned_midi_object(alignment)
    realigned_midi_object.write(write_path)


def export_alignment_to_wav(alignment, write_path):
    # type: (PureAligner.Alignment, str) -> ()
    realigned_midi_object = _get_realigned_midi_object(alignment)
    realigned_midi_audio = realigned_midi_object.fluidsynth(22050, FileHandler.SOUND_FONT_PATH)
    librosa.output.write_wav(write_path, realigned_midi_audio, 22050)
