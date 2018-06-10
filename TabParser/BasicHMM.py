from hmmlearn import hmm
from HMM import HMMParameters
import numpy as np
import Chords


class BasicHMM:
    def __init__(self, hmm_parameters):
        """

        :type hmm_parameters: HMMParameters
        """
        model = hmm.GaussianHMM(n_components=len(hmm_parameters.alphabet), covariance_type='full')
        model.startprob_ = hmm_parameters.init
        model.transmat_ = hmm_parameters.trans
        model.means_ = hmm_parameters.obs_mu
        model.covars_ = hmm_parameters.obs_sigma
        self.model = model
        self.alphabet = hmm_parameters.alphabet

    def predict_chord_labels(self, test_songs):
        result = []
        for test_song_key in test_songs:
            # Extract features
            features = np.load(test_songs[test_song_key].audio_features_path)
            chroma = features[:, 1:13].astype(float)
            ground_truth_labels = np.array(
                [self._get_index_in_alphabet(Chords.Chord.from_harte_chord_string(label)) for label in features[:, 13]])
            # Predict labels using HMM
            predicted_labels = self.model.predict(chroma)
            good_counter = 0
            bad_counter = 0
            for i in range(len(ground_truth_labels)):
                if predicted_labels[i] == ground_truth_labels[i]:
                    good_counter += 1
                else:
                    bad_counter += 1
            pseudo_acc = good_counter / float(good_counter + bad_counter)
            result.append(pseudo_acc)
        return result

    def _get_index_in_alphabet(self, chord):
        if len(self.alphabet) == 25:
            # Majmin alphabet
            if chord is None:
                chord_str = 'N'
            elif Chords.Interval(3) in chord.components_degree_list:
                chord_str = str(chord.root_note) + 'm'
            else:
                chord_str = str(chord.root_note)
            if chord_str not in self.alphabet:
                foutje = True
            return self.alphabet.index(chord_str)
        else:
            return 0  # Nog implementeren voor andere alphabets
