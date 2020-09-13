import matplotlib.pylab as pylab
import scipy.stats as ss
import matplotlib.pyplot as plt
import pandas
from decibel.import_export import filehandler
from os import path

params = {'legend.fontsize': 'xx-large',
          'figure.figsize': (15, 5),
          'axes.labelsize': 'xx-large',
          'axes.titlesize': 'xx-large',
          'xtick.labelsize': 'xx-large',
          'ytick.labelsize': 'xx-large'}
pylab.rcParams.update(params)


def figure_2():
    method_results_bar = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS['bar'], sep=';',
                                         names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
    method_results_beat = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS['beat'], sep=';',
                                          names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                 'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
    method_results_bar = method_results_bar[method_results_bar.alignment_error < 0.85]
    method_results_beat = method_results_beat[method_results_beat.alignment_error < 0.85]

    print('Beat: ' + str(ss.pearsonr(method_results_beat.wcsr, method_results_beat.template_sim)))
    print('Bar: ' + str(ss.pearsonr(method_results_bar.wcsr, method_results_bar.template_sim)))

    fig, axes = plt.subplots(ncols=2, figsize=(16, 8))
    # plt.figure(figsize=(10,10))
    axes[0].scatter(method_results_beat.template_sim, method_results_beat.wcsr)
    axes[1].scatter(method_results_bar.template_sim, method_results_bar.wcsr)
    fig.suptitle('CSR vs ATS, for all MIDI\'s with alignment error < 0.85', fontsize=25)
    axes[0].set_title('Beat Segmentation')
    axes[0].set_xlabel('ATS')
    axes[0].set_ylabel('CSR')
    axes[1].set_title('Bar Segmentation')
    axes[1].set_xlabel('ATS')
    axes[1].set_ylabel('CSR')
    plt.savefig(path.join(filehandler.RESULT_FIGURES, 'CSRvsATS'), bbox_inches='tight')


def figure_3(all_songs):
    method_results_bar = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS['bar'], sep=';',
                                         names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
    method_results_beat = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS['beat'], sep=';',
                                          names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                 'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
    # method_results_bar = method_results_bar[method_results_bar.alignment_error < 0.85]
    # method_results_beat = method_results_beat[method_results_beat.alignment_error < 0.85]

    all_est_beat = []
    all_csr_beat = []
    all_est_bar = []
    all_csr_bar = []

    for song_key in all_songs:
        method_results_bar_song = method_results_bar[method_results_bar.song_key == song_key]
        method_results_beat_song = method_results_beat[method_results_beat.song_key == song_key]

        if method_results_bar_song[method_results_bar_song.alignment_error < 0.85].shape[0] > 0 and \
                method_results_beat_song[method_results_beat_song.alignment_error < 0.85].shape[0] > 0:
            all_csr_bar.append(method_results_bar_song.wcsr.max())
            all_csr_beat.append(method_results_beat_song.wcsr.max())

            all_est_bar.append(method_results_bar_song.loc[
                                   method_results_bar_song[method_results_bar_song.alignment_error < 0.85][
                                       'template_sim'].idxmax()].wcsr)
            all_est_beat.append(method_results_beat_song.loc[
                                   method_results_beat_song[method_results_beat_song.alignment_error < 0.85][
                                       'template_sim'].idxmax()].wcsr)

    fig, ax = plt.subplots(ncols=2, figsize=(16, 8))
    ax[0].plot([0, 1], [0, 1], c='red')
    ax[0].scatter(all_est_beat, all_csr_beat)
    ax[0].set_title('Beat Segmentation')
    ax[0].set_xlabel('CSR of best estimated MIDI')
    ax[0].set_ylabel('CSR of best MIDI')

    ax[1].plot([0, 1], [0, 1], c='red')
    ax[1].scatter(all_est_bar, all_csr_bar)
    ax[1].set_title('Bar Segmentation')
    ax[1].set_xlabel('CSR of best estimated MIDI')
    ax[1].set_ylabel('CSR of best MIDI')

    fig.suptitle('CSR of best MIDI compared to CSR of best estimated MIDI', fontsize=25)
    plt.savefig(path.join(filehandler.RESULT_FIGURES, 'csr-ats-diff'), bbox_inches='tight')
