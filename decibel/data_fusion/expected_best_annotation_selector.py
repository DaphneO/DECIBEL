from decibel.data_fusion.annotation_selector_interface import AnnotationSelectorInterface


class ExpectedBestAnnotationSelector(AnnotationSelectorInterface):
    def select_annotations(self, input_annotations):
        return input_annotations

        # Get list of symbolic lab files (all / expected best)
        well_aligned_midis = filehandler.get_well_aligned_midis(song)
        all_symbolic_labs = \
            [filehandler.get_full_midi_chord_labs_path(wam, 'bar') for wam in well_aligned_midis] + \
            [filehandler.get_full_midi_chord_labs_path(wam, 'beat') for wam in well_aligned_midis] + \
            [filehandler.get_full_tab_chord_labs_path(t) for t in song.full_tab_paths]
        expected_best_symbolic_paths = []
        if well_aligned_midis:
            expected_best_symbolic_paths.append(
                filehandler.get_full_midi_chord_labs_path(*filehandler.get_expected_best_midi(song)))
        if [filehandler.get_full_tab_chord_labs_path(t) for t in song.full_tab_paths]:
            expected_best_symbolic_paths.append(
                filehandler.get_full_tab_chord_labs_path(filehandler.get_expected_best_tab_lab(song)))

        # Remove non-existing files (e.g. tab files in which too little chords were observed)
        all_symbolic_labs = [lab for lab in all_symbolic_labs if filehandler.file_exists(lab)]
        expected_best_symbolic_paths = [lab for lab in expected_best_symbolic_paths if filehandler.file_exists(lab)]

        # Get list of audio lab files
        audio_labs = song.full_mirex_chord_lab_paths
        audio_labs['CHF_2017'] = song.full_chordify_chord_labs_path
