import numpy as np
from decibel.tab_chord_parser.tablineclassifier import classify_lines
from decibel.tab_chord_parser.tabsegmenter import segment_line_list
from decibel.utils import filehandler


def classify_all_tabs_of_song(song) -> None:
    """
    Classify all tabs of a song, by (1) LineType classification; (2) Segmenting lines; (3) System and Chord extraction.
    
    :param song: A Song in our data set, for which we want to parse all tabs
    """
    for tab_path in song.full_tab_paths:
        write_path = filehandler.get_chords_from_tab_filename(tab_path)
        if not filehandler.file_exists(write_path):
            # Find all line types for this tab
            classified_lines = classify_lines(tab_path)
            # Segment them (by empty LineTypes)
            segments = segment_line_list(classified_lines)
            # Start with No chord symbol
            chord_lines = [[0, 0, 0, 0, 'N']]
            line_nr = 1
            for segment in segments:
                for system in segment.systems:
                    chords = system.chords
                    for chord_x, chord in chords:
                        # Add each chord line from each system in each segment
                        chord_lines.append([line_nr, segment.segment_nr, system.system_nr, chord_x, str(chord)])
                    line_nr += 1
            # End with No chord symbol
            chord_lines.append([line_nr, 0, 0, 0, 'N'])
            np.save(write_path, np.array(chord_lines))
