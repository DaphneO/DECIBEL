import librosa
import pretty_midi
import sys
import FileHandler


def _synthesize_midi_to_wav(midi_file_path_from, wav_file_path_to, sampling_rate=22050):
    """
    Converts a midi file, specified to its path, to a waveform and writes the result as a wav file
    :param midi_file_path_from: Path to the midi file which will be converted
    :param wav_file_path_to: Path to the wav file in which we will write te result
    :param sampling_rate: Sampling rate of the audio
    """
    midi_object = pretty_midi.PrettyMIDI(midi_file_path_from)
    midi_audio = midi_object.fluidsynth(sampling_rate, FileHandler.SOUND_FONT_PATH)
    librosa.output.write_wav(wav_file_path_to, midi_audio, sampling_rate)


def synthesize_all_midis_to_wav(all_songs, sampling_rate=22050):
    """
    Converts all midis belonging to all_songs to a waveform, writes the result to a wav file in wav_directory, adds
    paths to wav files to all_songs
    :param all_songs: All songs in our data set
    :param sampling_rate: Sampling rate of the audio
    """
    for song_nr in all_songs:
        midi_file_paths = all_songs[song_nr].full_midi_paths
        all_songs[song_nr].full_synthesized_midi_paths = []
        for midi_file_path_from in midi_file_paths:
            # Extract the filename (e.g. '001-001') from the path
            midi_file_name = FileHandler.get_file_name_from_full_path(midi_file_path_from)
            # Construct the path to write to
            wav_file_path_to = FileHandler.get_full_synthesized_midi_path(midi_file_name)
            # Check if we already synthesized this file
            if FileHandler.file_exists(wav_file_path_to):
                # We already synthesized this file in a previous run and will not do it again. Just add the path
                all_songs[song_nr].full_synthesized_midi_paths.append(wav_file_path_to)
            else:
                # The wav file does not yet exist, so we still have to synthesize this file
                try:
                    # Synthesize the midi
                    _synthesize_midi_to_wav(midi_file_path_from, wav_file_path_to, sampling_rate)
                    # We succeeded in synthesizing the midi, so we add this path to the full_synthesized_midi_paths
                    all_songs[song_nr].full_synthesized_midi_paths.append(wav_file_path_to)
                except:
                    print(midi_file_name + " could not be synthesized due to this error:", sys.exc_info()[0])
