# -*- coding: utf-8 -*-
from decibel.tab_chord_parser.lineclasses import LineType, Segment


def segment_line_list(line_list):
    """
    Takes a list of Lines and divides them into Segments, based on Empty LineTypes. Returns a list of them.

    :param line_list: List of Lines from a tab file
    :return: List of segments from a tab file
    """
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
