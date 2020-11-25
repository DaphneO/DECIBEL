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


def export_figures(all_songs):
    figure_2()
    figure_3(all_songs)
    figure_4(all_songs)


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
    plt.savefig(path.join(filehandler.FIGURES_PATH, 'CSRvsATS'), bbox_inches='tight')


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
    ax[0].plot([0, 1], [0, 1], c=plt.get_cmap("tab10").colors[1])
    ax[0].scatter(all_est_beat, all_csr_beat)
    ax[0].set_title('Beat Segmentation')
    ax[0].set_xlabel('CSR of best estimated MIDI')
    ax[0].set_ylabel('CSR of best MIDI')

    ax[1].plot([0, 1], [0, 1], c=plt.get_cmap("tab10").colors[1])
    ax[1].scatter(all_est_bar, all_csr_bar)
    ax[1].set_title('Bar Segmentation')
    ax[1].set_xlabel('CSR of best estimated MIDI')
    ax[1].set_ylabel('CSR of best MIDI')

    fig.suptitle('CSR of best MIDI compared to CSR of best estimated MIDI', fontsize=25)
    plt.savefig(path.join(filehandler.FIGURES_PATH, 'csr-ats-diff'), bbox_inches='tight')


def figure_4(all_songs):
    method_results_bar = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS['bar'], sep=';',
                                         names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
    wcsr_all_bar = []
    wcsr_selected_bar = []
    for song_key in all_songs:
        method_results_bar_song = method_results_bar[method_results_bar.song_key == song_key]
        wcsr_all_bar += list(method_results_bar_song.wcsr)
        well_aligned_bar_song = method_results_bar_song[method_results_bar_song.alignment_error <= 0.85]
        if not well_aligned_bar_song.empty:
            selected_midi_bar = well_aligned_bar_song.template_sim.idxmax()
            wcsr_selected_bar.append(well_aligned_bar_song.loc[selected_midi_bar].wcsr)

    method_results_beat = pandas.read_csv(filehandler.MIDILABS_RESULTS_PATHS['beat'], sep=';',
                                          names=['song_key', 'duration', 'midi_name', 'alignment_error', 'template_sim',
                                                 'wcsr', 'ovs', 'uns', 'seg'], index_col=2)
    wcsr_all_beat = []
    wcsr_selected_beat = []
    for song_key in all_songs:
        method_results_beat_song = method_results_beat[method_results_beat.song_key == song_key]
        wcsr_all_beat += list(method_results_beat_song.wcsr)
        well_aligned_beat_song = method_results_beat_song[method_results_beat_song.alignment_error <= 0.85]
        if not well_aligned_beat_song.empty:
            selected_midi_beat = well_aligned_beat_song.template_sim.idxmax()
            wcsr_selected_beat.append(well_aligned_beat_song.loc[selected_midi_beat].wcsr)

    method_results_tab = pandas.read_csv(filehandler.TABLABS_RESULTS_PATH, sep=';',
                                         names=['song_key', 'duration', 'tab_name', 'likelihood', 'transposition',
                                                'wcsr', 'overseg', 'underseg', 'seg'])
    wcsr_all_tab = []
    wcsr_selected_tab = []
    for song_key in all_songs:
        method_results_tab_song = method_results_tab[method_results_tab.song_key == song_key]
        wcsr_all_tab += list(method_results_tab_song.wcsr)
        if not method_results_tab_song.empty:
            selected_tab = method_results_tab_song.likelihood.idxmax()
            wcsr_selected_tab.append(method_results_tab_song.loc[selected_tab].wcsr)

    for song_key in all_songs:
        method_results_bar_song = method_results_bar[method_results_bar.song_key == song_key]
        method_results_beat_song = method_results_beat[method_results_beat.song_key == song_key]
        if method_results_bar_song.empty and method_results_beat_song.empty:
            print('There is no well-aligned midi for song ' + str(all_songs[song_key]))
        if method_results_bar_song.empty or method_results_beat_song.empty:
            print(str(all_songs[song_key]) + ' can only be well-aligned in at most one way.')
        method_results_tab_song = method_results_tab[method_results_tab.song_key == song_key]
        if method_results_tab_song.empty:
            print('There is no good tab for song ' + str(all_songs[song_key]))

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(21, 6))
    nr_bins = 49
    ax1.hist(wcsr_all_bar, bins=nr_bins, label='All')
    ax1.hist(wcsr_selected_bar, bins=nr_bins, label='Selected')
    ax1.legend(loc='upper left')
    ax1.set_title('MIDI-Bar CSR')
    ax1.set_xlabel('CSR')
    ax1.set_ylabel('Nr of MIDI files')
    ax2.hist(wcsr_all_beat, bins=nr_bins, label='All')
    ax2.hist(wcsr_selected_beat, bins=nr_bins, label='Selected')
    ax2.legend(loc='upper left')
    ax2.set_title('MIDI-Beat CSR')
    ax2.set_xlabel('CSR')
    ax2.set_ylabel('Nr of MIDI files')
    ax3.hist(wcsr_all_tab, bins=nr_bins, label='All')
    ax3.hist(wcsr_selected_beat, bins=nr_bins, label='Selected')
    ax3.legend(loc='upper left')
    ax3.set_title('Tab CSR')
    ax3.set_xlabel('CSR')
    ax3.set_ylabel('Nr of tab files')

    plt.savefig(path.join(filehandler.FIGURES_PATH, 'symbolic-csr-hist'), bbox_inches='tight')