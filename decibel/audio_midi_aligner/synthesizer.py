"""
The :py:mod:`decibel.audio_midi_aligner.synthesizer` module contains functions for synthesizing MIDI files using the
fluidsynth software synthesizer.
"""

import librosa
import pretty_midi
import decibel.utils.filehandler as fh


def synthesize_midi_to_wav(midi_file_path_from, sampling_rate=22050):
    """
    Converts a midi file, specified to its path, to a waveform and writes the result as a wav file

    :param midi_file_path_from: Path to the midi file which will be converted
    :param sampling_rate: Sampling rate of the audio
    """
    midi_file_name = fh.get_file_name_from_full_path(midi_file_path_from)
    wav_file_path_to = fh.get_full_synthesized_midi_path(midi_file_name)
    midi_object = pretty_midi.PrettyMIDI(midi_file_path_from)
    midi_audio = midi_object.fluidsynth(sampling_rate, fh.SOUND_FONT_PATH)
    librosa.output.write_wav(wav_file_path_to, midi_audio, sampling_rate)
