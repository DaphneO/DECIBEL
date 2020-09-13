import numpy as np

from decibel.music_objects.chord_alphabet import ChordAlphabet


class HMMParameters:
    def __init__(self, alphabet: ChordAlphabet, trans: np.ndarray, init: np.ndarray, obs_mu: np.ndarray,
                 obs_sigma: np.ndarray, log_det_sigma: np.ndarray, sigma_inverse: np.ndarray,
                 twelve_log_two_pi: np.float64):
        self.alphabet = alphabet
        self.trans = trans
        self.init = init
        self.obs_mu = obs_mu
        self.obs_sigma = obs_sigma
        self.log_det_sigma = log_det_sigma
        self.sigma_inverse = sigma_inverse
        self.twelve_log_two_pi = twelve_log_two_pi
