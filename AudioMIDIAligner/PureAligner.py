import librosa
import numpy as np
import numba
import scipy.spatial
import FileHandler

# CQT parameters
FS = 22050
NOTE_START = 36
N_NOTES = 48
HOP_LENGTH = 1024
# DTW parameters
GULLY = .96


def dtw(distance_matrix, gully=1., additive_penalty=0., multiplicative_penalty=1.):
    # type: (np.ndarray, float, float, float) -> (np.ndarray, np.ndarray, score)
    """ Compute the dynamic time warping distance between two sequences given a distance matrix.
    DTW score of lowest cost path through the distance matrix, including
    penalties.
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
    dtw_core(distance_matrix, additive_penalty, multiplicative_penalty, traceback)
    if gully < 1.:
        # Allow the end of the path to start within gully percentage of the smaller distance matrix dimension
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
    # type: (np.ndarray, float, float, np.ndarray) -> ()
    """Core dynamic programming routine for DTW.
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
    # type: (np.ndarray) -> (np.ndarray, np.ndarray)
    """ Compute the normalized log-amplitude CQT (Constant-Q transform) and frame times for the audio data
    :param audio_data: The audio data for which we compute the CQT
    :return: The CQT for the audio data and the time of each frame
    """
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
    def __init__(self, score, midi, alignment_path):
        # type: (float, str, (np.ndarray, np.ndarray)) -> ()
        """
        Initiates Alignment
        :param score: Quality of the alignment between 0 (perfect) and 1 (terrible)
        :param midi: Name of midi file of the alignment
        :param alignment_path: Optimal alignment path
        """
        self.score = score
        self.midi = midi
        self.alignment_path = alignment_path

    @classmethod
    def align_midi(cls, audio_cqt, audio_times, full_synthesized_midi_path):
        # type: (np.ndarray, np.ndarray, str) -> cls
        """
        Align audio (specified by CQT) to synthesized midi (specified by path), return path and score of the alignment
        :param audio_cqt: The CQT of the audio of the alignment
        :param audio_times: Array of times of the audio (from compute_cqt function)
        :param full_synthesized_midi_path: The path to the synthesized midi file
        :return: Optimal Alignment
        """
        # Open the synthesized midi file
        midi_audio, _ = librosa.load(full_synthesized_midi_path, sr=FS)
        # Compute log-magnitude CQT of the synthesized midi file
        midi_cqt, midi_times = compute_cqt(midi_audio)
        # Compute the distance matrix of the midi and audio CQTs, using cosine distance
        distance_matrix = scipy.spatial.distance.cdist(midi_cqt, audio_cqt, 'cosine')
        penalty = float(np.median(np.ravel(distance_matrix)))
        # Get lowest cost path in the distance matrix
        p, q, score = dtw(distance_matrix, GULLY, penalty)
        # Normalize by path length and the distance matrix sub-matrix within the path
        score = score / len(p)
        score = score / distance_matrix[p.min():p.max(), q.min():q.max()].mean()
        return cls(score, full_synthesized_midi_path, (midi_times[p], audio_times[q]))

    def write_alignment_result(self, write_path):
        # type: (str) -> ()
        """
        Write the Alignment to a file, in which the first line contains the score, the second contains the midi path
        and on the remaining lines we find the best alignment path
        :param write_path: Path to the file we'll write to
        """
        with open(write_path, 'w') as write_file:
            write_file.write(
                '{0}\n{1}\n'.format(str(self.score), str(self.midi)))
            for i in range(0, len(self.alignment_path[0])):
                write_file.write('{0} {1} {2}\n'.format(str(i),
                                                        str(self.alignment_path[0][i]), str(self.alignment_path[1][i])))

    @classmethod
    def from_alignment_file(cls, file_path):
        # type: (str) -> cls
        """
        Read the alignment from a file
        :param file_path: Path to the alignment file
        :return: The alignment, read from a file
        """
        with open(file_path, 'r') as read_file:
            lines = read_file.readlines()
            score = float(lines[0])
            midi = lines[1].replace('\n', '')
            p = []
            q = []
            for line in lines[2:]:
                line_parts = line.split()
                p.append(float(line_parts[1]))
                q.append(float(line_parts[2].replace('\n', '')))
            return cls(score, midi, (p, q))


def align_midis(all_songs):
    # type: (dict)-> ()
    """
    Add the alignments to the midi files to all_songs
    :param all_songs: All songs in our dataset
    """
    for song_nr in all_songs:
        song = all_songs[song_nr]
        audio_loaded = False
        audio_cqt = np.ndarray([])
        audio_times = np.ndarray([])
        for midi_path in song.full_synthesized_midi_paths:
            midi_file_name = FileHandler.get_file_name_from_full_path(midi_path)
            write_path = FileHandler.get_full_alignment_path(midi_file_name)
            if not FileHandler.file_exists(write_path):
                # There is no alignment yet for this audio-midi combination, so let's calculate the alignment
                try:
                    if not audio_loaded:
                        # Load audio if it is not loaded yet
                        audio_data, _ = librosa.load(song.full_audio_path, sr=FS)
                        audio_cqt, audio_times = compute_cqt(audio_data)
                        audio_loaded = True
                    a = Alignment.align_midi(audio_cqt, audio_times, midi_path)
                    a.write_alignment_result(write_path)
                    song.midi_alignments.append(a)
                except:
                    print(write_path + " failed.")
            else:
                # We already calculated this alignment so we can read a previous result
                a = Alignment.from_alignment_file(write_path)
                song.midi_alignments.append(a)
