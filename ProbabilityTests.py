# In these tests, we try to find the optimal forward and backward probability for Jump Alignment.
# We test this for 22 songs (specified in SubsetCorrectTransposition.txt) for which we are sure they are in the right
# key, so we do not need to transpose the tabs and find the best transposition.
import numpy as np
import Evaluator

def find_forward_and_backward_probabilities(all_songs, hmm_parameters):
    with open('/media/daphne/Seagate Expansion Drive/Data/ProbabilityTestResults/SubsetCorrectTranspositionTabs.txt',
              'r') as keys_and_tabs:
        lines = keys_and_tabs.readlines()
    likelihoods = np.zeros((21, 21))
    roots = np.zeros((21, 21))
    maj_mins = np.zeros((21, 21))
    with open('/media/daphne/Seagate Expansion Drive/Data/ProbabilityTestResults/Results.txt', 'w') as write_file:
        for line in lines:
            parts = line.split('\t')
            key = int(parts[0])
            song = all_songs[key]
            tab_name = parts[1].rstrip()

            audio_features_path = all_songs[key].audio_features_path
            tab_chord_path = '/media/daphne/Seagate Expansion Drive/Data/ChordsFromTabs/' + \
                             tab_name.replace('.txt','.npy')

            for p_f_t in range(0, 101, 5):
                for p_b_t in range(0, 101, 5):
                    p_f = 0.01 * p_f_t
                    p_b = 0.01 * p_b_t
                    tab_write_path = '/media/daphne/Seagate Expansion Drive/Data/ProbabilityTestResults/' + \
                                     tab_name[:-4] + str(p_f_t) + '-' + str(p_b_t) + '.txt'
                    log_likelihood = \
                        hmm_parameters.jump_alignment(tab_chord_path, audio_features_path, tab_write_path, p_f, p_b)
                    s1, s2, s3 = Evaluator.evaluate(song.full_chord_labs_path, tab_write_path)
                    write_file.write('{0};{1};{2};{3};{4};{5};{6};{7}\n'.format(str(key), str(tab_write_path),
                                                                            str(p_f), str(p_b), str(log_likelihood),
                                                                            str(s1), str(s2), str(s3)))
                    likelihoods[int(20 * p_f), int(20 * p_b)] += log_likelihood
                    roots[int(20 * p_f), int(20 * p_b)] += s1
                    maj_mins[int(20 * p_f), int(20 * p_b)] += s2

    np.save('/media/daphne/Seagate Expansion Drive/Data/ProbabilityTestResults/AggResults.txt', np.c_[likelihoods, roots, maj_mins])