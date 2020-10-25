"""
The :py:mod:`decibel.audio_midi_aligner.aligner` module contains functions for finding the alignment between the
synthesized MIDI file and the audio recording. The :py:func:`align_midi` function (in the Alignment class) finds the
alignment between a single MIDI file and the matched audio recording and returns an Alignment object.
The function :py:func:`align_single_song` finds the alignment between the audio file of the given song and all matched
MIDI files.
Since this can take a long time, it is possible to interrupt and resume this process: all MIDI files that are aligned,
are stored and can be reloaded quickly when they are needed in a new program run.
"""
from typing import Optional, Tuple

import librosa
import numpy as np
from numba import jit
import scipy.spatial
import decibel.import_export.filehandler as fh
import decibel.import_export.midi_alignment_score_io
import decibel.import_export.midi_alignment_io
from decibel.audio_midi_aligner import synthesizer
from decibel.audio_midi_aligner.alignment_parameters import AlignmentParameters
from decibel.audio_midi_aligner.midi_alignment import MIDIAlignment
from decibel.music_objects.song import Song


def _dtw(distance_matrix: np.ndarray, gully: float = 1., additive_penalty: float = 0.,
         multiplicative_penalty: float = 1.) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Compute the dynamic time warping distance between two sequences given a distance matrix.
    DTW score of lowest cost path through the distance matrix, including penalties.

    :param distance_matrix: Distances between two sequences
    :param gully: Sequences must match up to this proportion of the shorter sequence.
    Default value is 1, which means that the entirety of the shorter sequence must be matched to a part of the
    longer sequence.
    :param additive_penalty: Additive penalty for non-diagonal moves.
    Default value is 0, which means no penalty.
    :param multiplicative_penalty: Multiplicative penalty for non-diagonal moves.
    Default value is 1, which means no penalty.
    :return: Lowest cost path through the distance matrix. Penalties are included, the score is not yet normalized.
    """
    if np.isnan(distance_matrix).any():
        raise ValueError('NaN values found in distance matrix.')
    distance_matrix = distance_matrix.copy()
    # Pre-allocate path length matrix
    traceback = np.empty(distance_matrix.shape, np.uint8)
    # Populate distance matrix with lowest cost path
    _dtw_core(distance_matrix, additive_penalty, multiplicative_penalty, traceback)
    if gully < 1.:
        # Allow the end of the path to start within gully percentage of the smaller distance matrix dimension
        gully = int(gully * min(distance_matrix.shape))
    else:
        # When gully is 1 require matching the entirety of the smaller sequence
        gully = min(distance_matrix.shape) - 1

    # Find the indices of the smallest costs on the bottom and right edges
    i = np.argmin(distance_matrix[gully:, -1]) + gully
    j = np.argmin(distance_matrix[-1, gully:]) + gully

    # Choose the smaller cost on the two edges
    if distance_matrix[-1, j] > distance_matrix[i, -1]:
        j = distance_matrix.shape[1] - 1
    else:
        i = distance_matrix.shape[0] - 1

    # Score is the final score of the best path
    score = float(distance_matrix[i, j])

    # Pre-allocate the x and y path index arrays
    x_indices = np.zeros(sum(traceback.shape), dtype=np.int)
    y_indices = np.zeros(sum(traceback.shape), dtype=np.int)
    # Start the arrays from the end of the path
    x_indices[0] = i
    y_indices[0] = j
    # Keep track of path length
    n = 1

    # Until we reach an edge
    while i > 0 and j > 0:
        # If the tracback matrix indicates a diagonal move...
        if traceback[i, j] == 0:
            i = i - 1
            j = j - 1
        # Horizontal move...
        elif traceback[i, j] == 1:
            i = i - 1
        # Vertical move...
        elif traceback[i, j] == 2:
            j = j - 1
        # Add these indices into the path arrays
        x_indices[n] = i
        y_indices[n] = j
        n += 1
    # Reverse and crop the path index arrays
    x_indices = x_indices[:n][::-1]
    y_indices = y_indices[:n][::-1]

    return x_indices, y_indices, score


@jit(nopython=True)
def _dtw_core(dist_mat: np.ndarray, add_pen: float, mul_pen: float, traceback: np.ndarray):
    """
    Core dynamic programming routine for DTW.
    `dist_mat` and `traceback` will be modified in-place.

    :param dist_mat: Distance matrix to update with lowest-cost path to each entry
    :param add_pen: Additive penalty for non-diagonal moves
    :param mul_pen: Multiplicative penalty for non-diagonal moves
    :param traceback: Matrix to populate with the lowest-cost traceback for each entry
    """
    # At each loop iteration, we are computing lowest cost to D[i + 1, j + 1]
    for i in range(dist_mat.shape[0] - 1):
        for j in range(dist_mat.shape[1] - 1):
            # Diagonal move (which has no penalty) is lowest
            if dist_mat[i, j] <= mul_pen * dist_mat[i, j + 1] + add_pen and \
                    dist_mat[i, j] <= mul_pen * dist_mat[i + 1, j] + add_pen:
                traceback[i + 1, j + 1] = 0
                dist_mat[i + 1, j + 1] += dist_mat[i, j]
            # Horizontal move (has penalty)
            elif (dist_mat[i, j + 1] <= dist_mat[i + 1, j] and
                  mul_pen * dist_mat[i, j + 1] + add_pen <= dist_mat[i, j]):
                traceback[i + 1, j + 1] = 1
                dist_mat[i + 1, j + 1] += mul_pen * dist_mat[i, j + 1] + add_pen
            # Vertical move (has penalty)
            elif (dist_mat[i + 1, j] <= dist_mat[i, j + 1] and
                  mul_pen * dist_mat[i + 1, j] + add_pen <= dist_mat[i, j]):
                traceback[i + 1, j + 1] = 2
                dist_mat[i + 1, j + 1] += mul_pen * dist_mat[i + 1, j] + add_pen


def _compute_cqt(audio_data: np.ndarray, alignment_parameters: AlignmentParameters) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the normalized log-amplitude CQT (Constant-Q transform) and frame times for the audio data

    :param audio_data: The audio data for which we compute the CQT
    :return: The CQT for the audio data and the time of each frame
    """
    # Compute CQT
    cqt = librosa.cqt(audio_data,
                      sr=alignment_parameters.sampling_rate,
                      fmin=librosa.midi_to_hz(alignment_parameters.lowest_midi_note),
                      n_bins=alignment_parameters.nr_of_midi_notes,
                      hop_length=alignment_parameters.hop_length,
                      tuning=0.)
    # Compute the time of each frame
    times = librosa.frames_to_time(
        np.arange(cqt.shape[1]), sr=alignment_parameters.sampling_rate, hop_length=alignment_parameters.hop_length)
    # Compute log-amplitude
    cqt = librosa.amplitude_to_db(cqt, ref=cqt.max())
    # Normalize and return
    return librosa.util.normalize(cqt, 2).T, times


def align_midi(audio_cqt: np.ndarray, audio_times: np.ndarray, full_synthesized_midi_path: str,
               full_alignment_write_path: str, alignment_parameters: Optional[AlignmentParameters] = None):
    """
    Align audio (specified by CQT) to synthesized MIDI (specified by path), return path and score of the alignment

    :param alignment_parameters: Parameters for alignment
    :param audio_cqt: The CQT of the audio of the alignment
    :param audio_times: Array of times of the audio (from compute_cqt function)
    :param full_synthesized_midi_path: The path to the synthesized MIDI file
    :param full_alignment_write_path: The path to write the alignment to
    """
    # Make sure to have alignment parameters
    if alignment_parameters is None:
        alignment_parameters = AlignmentParameters()
    # Open the synthesized midi file
    midi_audio, _ = librosa.load(full_synthesized_midi_path, sr=alignment_parameters.sampling_rate)
    # Compute log-magnitude CQT of the synthesized midi file
    midi_cqt, midi_times = _compute_cqt(midi_audio, alignment_parameters)
    # Compute the distance matrix of the midi and audio CQTs, using cosine distance
    distance_matrix = scipy.spatial.distance.cdist(midi_cqt, audio_cqt, 'cosine')
    additive_penalty = float(np.median(np.ravel(distance_matrix)))
    multiplicative_penalty = 1.
    # Get lowest cost path in the distance matrix
    p, q, score = _dtw(distance_matrix, alignment_parameters.gully, additive_penalty, multiplicative_penalty)

    # Compute MIDIAlignment
    midi_alignment = MIDIAlignment(midi_times.__getitem__(p), audio_times.__getitem__(q))

    # Normalize by path length and the distance matrix sub-matrix within the path
    score = score / len(p)
    score = score / distance_matrix[p.min():p.max(), q.min():q.max()].mean()

    # Write score
    midi_name = fh.get_file_name_from_full_path(full_synthesized_midi_path)
    decibel.import_export.midi_alignment_score_io.write_chord_alignment_score(midi_name, score)

    # Write alignment
    decibel.import_export.midi_alignment_io.write_alignment_file(midi_alignment, full_alignment_write_path)
    # with open(full_alignment_write_path, 'w') as write_file:
    #     for i in range(len(p)):
    #         write_file.write('{0} {1} {2}\n'.format(str(i), str(midi_times[p[i]]), str(audio_times[q[i]])))


def align_single_song(song: Song, alignment_parameters: Optional[AlignmentParameters] = None):
    """
    Align each MIDI file that is matched to this song to the song. As part of the procedure, each MIDI will be
    synthesized and the alignment of each MIDI will be written to a file.

    :param alignment_parameters: Parameters for alignment
    :param song: The Song object for which we align each MIDI file
    """
    # Make sure to have alignment parameters
    if alignment_parameters is None:
        alignment_parameters = AlignmentParameters()

    audio_loaded = False
    audio_cqt = np.ndarray([])
    audio_times = np.ndarray([])

    for midi_path in song.full_midi_paths:
        midi_name = fh.get_file_name_from_full_path(midi_path)
        write_path = fh.get_full_alignment_path(midi_name)
        if not fh.file_exists(write_path):
            # There is no alignment yet for this audio-midi combination, so let's calculate the alignment
            try:
                synthesized_midi_path = fh.get_full_synthesized_midi_path(midi_name)
                if not fh.file_exists(synthesized_midi_path):
                    # The MIDI has not been synthesized yet
                    synthesizer.synthesize_midi_to_wav(midi_path, alignment_parameters.sampling_rate)

                if not audio_loaded:
                    # Load audio if it is not loaded yet
                    audio_data, _ = librosa.load(song.full_audio_path, sr=alignment_parameters.sampling_rate)
                    audio_cqt, audio_times = _compute_cqt(audio_data, alignment_parameters)
                    audio_loaded = True
                align_midi(audio_cqt, audio_times, synthesized_midi_path, write_path, alignment_parameters)
                fh.remove_file(synthesized_midi_path)
            except:
                print(write_path + " failed.")
