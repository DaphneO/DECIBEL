import pretty_midi
import librosa
import PureAligner
import FileHandler

# Note: these functions are not used in the main pipeline, but can be used in order to test the quality of the
# alignment. For example:
# 1) Export the realigned MIDI to .wav using export_alignment_to_wav
# 2) Load this .wav file in Sonic Visualiser
# 3) Load the original audio file in Sonic Visualizer too
# 4) Listen to both audio files at the same time: you can hear if they are aligned well


def _get_realigned_midi_object(alignment):
    # type: (PureAligner.Alignment) -> pretty_midi.PrettyMIDI
    """
    Find the MIDI object that is realigned using the specified alignment
    :param alignment: Alignment object, which we use to realign the MIDI
    :return: Realigned MIDI object
    """
    # Load original MIDI into pretty_midi object
    synthesized_midi_path = alignment.midi
    midi_name = FileHandler.get_file_name_from_full_path(synthesized_midi_path)
    midi_path = FileHandler.get_full_midi_path(midi_name)
    midi_object = pretty_midi.PrettyMIDI(midi_path)
    # Realign: adjust the MIDI times
    midi_object.adjust_times(alignment.alignment_path[0], alignment.alignment_path[1])
    # Remove any notes whose end time is before or at their start time
    midi_object.remove_invalid_notes()
    return midi_object


def export_alignment_to_midi(alignment, write_path):
    # type: (PureAligner.Alignment, str) -> None
    """
    Realign a midi to a .mid file using the specified alignment
    :param alignment: Alignment object, which we use to realign the MIDI
    :param write_path: Location to which we will write the .mid file
    """
    realigned_midi_object = _get_realigned_midi_object(alignment)
    realigned_midi_object.write(write_path)


def export_alignment_to_wav(alignment, write_path):
    # type: (PureAligner.Alignment, str) -> None
    """
    Realign a midi and synthesize to a .wav file using the specified alignment
    :param alignment: Alignment object, which we use to realign the MIDI
    :param write_path: Location to which we will write the .wav file
    """
    realigned_midi_object = _get_realigned_midi_object(alignment)
    realigned_midi_audio = realigned_midi_object.fluidsynth(22050, FileHandler.SOUND_FONT_PATH)
    librosa.output.write_wav(write_path, realigned_midi_audio, 22050)
