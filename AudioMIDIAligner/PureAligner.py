import librosa
import numpy as np
import numba
import pretty_midi
import scipy.spatial

FS = 22050
NOTE_START = 36
N_NOTES = 48
HOP_LENGTH = 1024
# DTW parameters
GULLY = .96


def dtw(distance_matrix, gully=1., additive_penalty=0.,
        multiplicative_penalty=1., mask=None, inplace=True):
    """ Compute the dynamic time warping distance between two sequences given a
    distance matrix.  The score is unnormalized.

    Parameters
    ----------
    distance_matrix : np.ndarray
        Distances between two sequences.
    gully : float
        Sequences must match up to this porportion of shorter sequence. Default
        1., which means the entirety of the shorter sequence must be matched
        to part of the longer sequence.
    additive_penalty : int or float
        Additive penalty for non-diagonal moves. Default 0. means no penalty.
    multiplicative_penalty : int or float
        Multiplicative penalty for non-diagonal moves. Default 1. means no
        penalty.
    mask : np.ndarray
        A boolean matrix, such that ``mask[i, j] == 1`` when the index ``i, j``
        should be allowed in the DTW path and ``mask[i, j] == 0`` otherwise.
        If None (default), don't apply a mask - this is more efficient than
        providing a mask of all 1s.
    inplace : bool
        When ``inplace == True`` (default), `distance_matrix` will be modified
        in-place when computing path costs.  When ``inplace == False``,
        `distance_matrix` will not be modified.

    Returns
    -------
    x_indices : np.ndarray
        Indices of the lowest-cost path in the first dimension of the distance
        matrix.
    y_indices : np.ndarray
        Indices of the lowest-cost path in the second dimension of the distance
        matrix.
    score : float
        DTW score of lowest cost path through the distance matrix, including
        penalties.
    """
    if np.isnan(distance_matrix).any():
        raise ValueError('NaN values found in distance matrix.')
    if not inplace:
        distance_matrix = distance_matrix.copy()
    # Pre-allocate path length matrix
    traceback = np.empty(distance_matrix.shape, np.uint8)
    # Don't use masked DTW routine if no mask was provided
    if mask is None:
        # Populate distance matrix with lowest cost path
        dtw_core(distance_matrix, additive_penalty, multiplicative_penalty,
                 traceback)
    if gully < 1.:
        # Allow the end of the path to start within gully percentage of the
        # smaller distance matrix dimension
        gully = int(gully*min(distance_matrix.shape))
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


@numba.jit(nopython=True)
def dtw_core(dist_mat, add_pen, mul_pen, traceback):
    """Core dynamic programming routine for DTW.

    `dist_mat` and `traceback` will be modified in-place.

    Parameters
    ----------
    dist_mat : np.ndarray
        Distance matrix to update with lowest-cost path to each entry.
    add_pen : int or float
        Additive penalty for non-diagonal moves.
    mul_pen : int or float
        Multiplicative penalty for non-diagonal moves.
    traceback : np.ndarray
        Matrix to populate with the lowest-cost traceback from each entry.
    """
    # At each loop iteration, we are computing lowest cost to D[i + 1, j + 1]
    # TOOD: Would probably be faster if xrange(1, dist_mat.shape[0])
    for i in range(dist_mat.shape[0] - 1):
        for j in range(dist_mat.shape[1] - 1):
            # Diagonal move (which has no penalty) is lowest
            if dist_mat[i, j] <= mul_pen*dist_mat[i, j + 1] + add_pen and \
               dist_mat[i, j] <= mul_pen*dist_mat[i + 1, j] + add_pen:
                traceback[i + 1, j + 1] = 0
                dist_mat[i + 1, j + 1] += dist_mat[i, j]
            # Horizontal move (has penalty)
            elif (dist_mat[i, j + 1] <= dist_mat[i + 1, j] and
                  mul_pen*dist_mat[i, j + 1] + add_pen <= dist_mat[i, j]):
                traceback[i + 1, j + 1] = 1
                dist_mat[i + 1, j + 1] += mul_pen*dist_mat[i, j + 1] + add_pen
            # Vertical move (has penalty)
            elif (dist_mat[i + 1, j] <= dist_mat[i, j + 1] and
                  mul_pen*dist_mat[i + 1, j] + add_pen <= dist_mat[i, j]):
                traceback[i + 1, j + 1] = 2
                dist_mat[i + 1, j + 1] += mul_pen*dist_mat[i + 1, j] + add_pen


def compute_cqt(audio_data):
    """ Compute the CQT and frame times for some audio data """
    # Compute CQT
    cqt = librosa.cqt(audio_data, sr=FS, fmin=librosa.midi_to_hz(NOTE_START),
                      n_bins=N_NOTES, hop_length=HOP_LENGTH, tuning=0.)
    # Compute the time of each frame
    times = librosa.frames_to_time(
        np.arange(cqt.shape[1]), sr=FS, hop_length=HOP_LENGTH)
    # Compute log-amplitude
    cqt = librosa.amplitude_to_db(cqt, ref=cqt.max())
    # Normalize and return
    return librosa.util.normalize(cqt, 2).T, times


class Alignment:
    def __init__(self, song):
        audio_data, _ = librosa.load(song.full_audio_path, sr=FS)
        audio_cqt, audio_times = compute_cqt(audio_data)
        self.best_score = 2
        self.best_path = None
        self.best_midi = None
        for full_synthesized_midi_path in song.full_synthesized_midi_paths:
            p, q, score = align_midi(audio_cqt, full_synthesized_midi_path)
            if score < self.best_score:
                self.best_score = score
                self.best_path = (p, q)
                self.best_midi = full_synthesized_midi_path

    def write_alignment_result(self, wp):
        with open(wp, 'w') as write_file:
            write_file.write(
                '{0}\n{1}\n'.format(str(self.best_score), str(self.best_midi)))
            for i in range(0, len(self.best_path[0])):
                write_file.write('{0} {1} {2}\n'.format(str(i), str(self.best_path[0][i]), str(self.best_path[1][i])))



def align_midis(all_songs):
    for song_nr in all_songs:
        a = Alignment(all_songs[song_nr])
        a.write_alignment_result('E:\\Data\\alignmentpath.txt')
        klaar = True

def align_midi(audio_cqt, full_synthesized_midi_path):
    midi_audio, _ = librosa.load(full_synthesized_midi_path, sr=FS)
    # Compute log-magnitude CQT
    midi_cqt, midi_times = compute_cqt(midi_audio)
    # Nearly all high-performing systems used cosine distance
    distance_matrix = scipy.spatial.distance.cdist(
        midi_cqt, audio_cqt, 'cosine')
    penalty = float(np.median(np.ravel(distance_matrix)))
    # Get lowest cost path
    p, q, score = dtw(
        distance_matrix,
        # The gully for all high-performing systems was near 1
        GULLY,
        # The penalty was also near 1.0*median(distance_matrix)
        penalty,
        # Don't modify the distance matrix in place, as we will
        # use it to normalize the score below
        inplace=False)
    # Normalize by path length
    score = score/len(p)
    # Normalize by distance matrix submatrix within path
    score = score/distance_matrix[p.min():p.max(), q.min():q.max()].mean()
    return p, q, score
