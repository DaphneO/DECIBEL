import librosa
import numpy as np
import mir_eval
from decibel.utils import filehandler


def _find_longest_chord_per_beat(beats: np.ndarray, ref_intervals: np.ndarray, ref_labels: np.ndarray):
    """
    Beat-synchronize the reference chord annotations, by assigning the chord with the longest duration within that beat

    :param beats: Array of beats, measured in seconds
    :param ref_intervals: Array of (start-time, end-time) intervals
    :param ref_labels: Array of chord labels belonging to the ref_intervals
    :return: List of chords within each beat
    """
    # Find start and end locations of each beat
    beat_starts = beats[:-1]
    beat_ends = beats[1:]

    # Create the longest_chords list, which we will fill in the for loop
    longest_chords = []
    for i in range(beat_starts.size):
        # Iterate over the beats in this song, keeping the chord with the longest duration
        b_s = beat_starts[i]
        b_e = beat_ends[i]
        longest_chord_duration = 0
        longest_chord = 'N'
        for j in range(ref_intervals.shape[0]):
            # Iterate over the intervals in the reference chord annotations
            r_s = ref_intervals[j][0]  # Start time of reference interval
            r_e = ref_intervals[j][1]  # End time of reference interval
            if r_s < b_e and r_e > b_s:
                # This reference interval overlaps with the current beat
                start_inside_beat = max(r_s, b_s)
                end_inside_beat = min(r_e, b_e)
                duration_inside_beat = end_inside_beat - start_inside_beat
                if duration_inside_beat > longest_chord_duration:
                    longest_chord_duration = duration_inside_beat
                    longest_chord = ref_labels[j]
        # Add the chord with the longest duration to our list
        longest_chords.append(longest_chord)
    return longest_chords


def export_audio_features(song) -> None:
    """
    Export the audio features of this song to a file.

    For this purpose, we use the python package librosa. First, we convert the audio file to mono. Then, we use the
    HPSS function to separate the harmonic and percussive elements of the audio. Then, we extract chroma from the
    harmonic part, using constant-Q transform with a sampling rate of 22050 and a hop length of 256 samples. Now we
    have chroma features for each sample, but we expect that the great majority of chord changes occurs on a beat.
    Therefore, we beat-synchronize the features: we run a beat-extraction function on the percussive part of the audio
    and average the chroma features between the consecutive beat positions. The chord annotations need to be
    beat-synchronized as well. We do this by taking the most prevalent chord label between beats. Each mean feature
    vector with the corresponding beat-synchronized chord label is regarded as one frame.

    :param song: Song for which we export the audio features
    """
    if song.full_ground_truth_chord_labs_path != '':
        # There are chord labels for this song
        write_path = filehandler.get_full_audio_features_path(song.key)
        if filehandler.file_exists(write_path):
            # We already extracted the audio features
            song.audio_features_path = write_path
        else:
            # We did not extract the audio features yet
            sampling_rate = 22050
            hop_length = 256

            # Load audio with small sampling rate and convert to mono. Audio is an array with a value per *sample*
            audio, _ = librosa.load(song.full_audio_path, sr=sampling_rate, mono=True)

            # Separate harmonics and percussives into two waveforms. We get two arrays, each with one value per *sample*
            audio_harmonic, audio_percussive = librosa.effects.hpss(audio)

            # Beat track on the percussive signal. The result is an array of *frames* which are on a beat
            _, beat_frames = librosa.beat.beat_track(y=audio_percussive, sr=sampling_rate, hop_length=hop_length,
                                                     trim=False)

            # Compute chroma features from the harmonic signal. We get a 12D array of chroma for each *frame*
            chromagram = librosa.feature.chroma_cqt(y=audio_harmonic, sr=sampling_rate, hop_length=hop_length)

            # Make sure the last beat is not longer than the length of the chromagram
            beat_frames = librosa.util.fix_frames(beat_frames, x_max=chromagram.shape[1])

            # Aggregate chroma features between *beat events*. We use the mean value of each feature between beat frames
            beat_chroma = librosa.util.sync(chromagram, beat_frames)
            beat_chroma = np.transpose(beat_chroma)

            # Translate beats from frames to time domain
            beats = librosa.frames_to_time(beat_frames, sr=sampling_rate, hop_length=hop_length)

            # Load chords from ground truth file
            (ref_intervals, ref_labels) = mir_eval.io.load_labeled_intervals(song.full_ground_truth_chord_labs_path)

            # Decide for every beat which chord has the longest duration within that beat
            longest_chords_per_beat = _find_longest_chord_per_beat(beats, ref_intervals, ref_labels)

            # Combine the beat times, chroma values and chord labels into a matrix with 14 columns and |beats| rows
            times_features_class = np.c_[beats[:-1], beat_chroma, longest_chords_per_beat]

            # Export the beat, feature and class matrix to the write_path (a binary .npy file)
            song.audio_features_path = write_path
            np.save(write_path, times_features_class)
