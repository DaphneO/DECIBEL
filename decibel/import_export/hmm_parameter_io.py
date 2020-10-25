import json

import numpy as np

from decibel.audio_tab_aligner.hmm_parameters import HMMParameters

from json import JSONEncoder, JSONDecoder

from decibel.music_objects.chord_alphabet import ChordAlphabet
from decibel.music_objects.chord_vocabulary import ChordVocabulary


class HMMParametersEncoder(JSONEncoder):
    def default(self, hmm_parameters: HMMParameters):
        return {
            'alphabet_name': hmm_parameters.alphabet.chord_vocabulary_name,
            'trans': hmm_parameters.trans.tolist(),
            'init': hmm_parameters.init.tolist(),
            'obs_mu': hmm_parameters.obs_mu.tolist(),
            'obs_sigma': hmm_parameters.obs_sigma.tolist(),
            'log_det_sigma': hmm_parameters.log_det_sigma.tolist(),
            'sigma_inverse': hmm_parameters.sigma_inverse.tolist(),
            'twelve_log_two_pi': hmm_parameters.twelve_log_two_pi,
            'trained_on_keys': hmm_parameters.trained_on_keys
        }


class HMMParametersDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        chord_alphabet = ChordAlphabet(ChordVocabulary.from_name(obj['alphabet_name']))

        return HMMParameters(
            alphabet=chord_alphabet,
            trans=np.asarray(obj['trans']),
            init=np.asarray(obj['init']),
            obs_mu=np.asarray(obj['obs_mu']),
            obs_sigma=np.asarray(obj['obs_sigma']),
            log_det_sigma=np.asarray(obj['log_det_sigma']),
            sigma_inverse=np.asarray(obj['sigma_inverse']),
            twelve_log_two_pi=obj['twelve_log_two_pi'],
            trained_on_keys=obj['trained_on_keys']
        )


def read_hmm_parameters_file(file_path: str) -> HMMParameters:
    """
    Read the HMMParameters from a file

    :param file_path: Path to the HMMParameters
    :return: The HMMParameters, read from a file
    """
    with open(file_path, 'r') as read_file:
        return json.load(cls=HMMParametersDecoder, fp=read_file)


def write_hmm_parameters_file(hmm_parameters: HMMParameters, file_path: str):
    with open(file_path, 'w') as write_file:
        json.dump(hmm_parameters, cls=HMMParametersEncoder, fp=write_file)
