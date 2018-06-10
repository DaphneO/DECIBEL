# -*- coding: utf-8 -*-
# from TabParser import TabLineClassifier
# from TabParser.TabLineClassifier import LineType
# from Chords import *
# import ChordTemplateGenerator
# import scipy.spatial.distance as ssd
# import re

from LineClasses import LineType, Segment


def segment_line_list(line_list):
    """Takes a list of Lines and divides them into Segments, based on Empty LineTypes. Returns a list of them."""
    result = []
    segment_nr = 0
    new_segment = True
    for line in line_list:
        if line.line_type == LineType.Empty:
            if not new_segment:
                new_segment = True
                segment_nr += 1
        else:
            if new_segment:
                result.append(Segment(segment_nr))
                new_segment = False
            result[segment_nr].add_line(line)

    for segment in result:
        segment.find_systems()

    return result


# Divide the lines into segments, defined as all lines between lines with Empty LineType
# segments_for_all_songs = dict()
# for song_name in line_list_for_all_songs:
#     line_list = line_list_for_all_songs[song_name]
#     segments_for_all_songs[song_name] = segment_line_list(line_list)

# # Find the systems in all segments
# ALL_CHORDS_LIST = ChordTemplateGenerator.generate_chroma_all_chords()
# final_result = open('E:\Data\Tabs\AllChordsAndLyrics.csv', 'w', encoding='utf-8')
# systems_for_all_songs = dict()
# for song_name in segments_for_all_songs:
#     systems_for_all_songs[song_name] = []
#     segment_list = segments_for_all_songs[song_name]
#     for segment in segment_list:
#         segment.find_systems()
#         for system in segment.systems:
#             systems_for_all_songs[song_name].append(system)
#             for (x, c) in system.chords:
#                 final_result.write(song_name + ';' + str(segment.segment_nr) + ';' + str(system.system_nr)
#                                    + ';' + str(x) + ';' + str(c) + ';Chord\n')
#             for (x, l) in system.lyrics:
#                 final_result.write(song_name + ';' + str(segment.segment_nr) + ';' + str(system.system_nr)
#                                    + ';' + str(x) + ';' + str(l) + ';Word\n')
# final_result.close()