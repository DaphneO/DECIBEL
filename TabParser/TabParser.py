from TabLineClassifier import classify_lines
from TabSegmenter import segment_line_list
import numpy as np
import FileHandler


def classify_all_tabs(all_songs):
    for song_key in all_songs:
        song = all_songs[song_key]
        for tab_path in song.full_tab_paths:
            write_path = FileHandler.get_chords_from_tab_filename(tab_path)
            if not FileHandler.file_exists(write_path):
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
