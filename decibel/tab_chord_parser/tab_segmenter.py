# -*- coding: utf-8 -*-
from typing import List

from decibel.tab_chord_parser.segment import Segment
from decibel.tab_chord_parser.line_type import LineType
from decibel.tab_chord_parser.line import Line
from decibel.tab_chord_parser.system import System


def find_systems(segment: Segment):
    system_nr = 0
    system_line_nr = 0
    while system_line_nr < len(segment.lines):
        line = segment.lines[system_line_nr]
        if line.line_type == LineType.ChordsAndLyrics:
            segment.add_system(System(system_nr))
            segment.systems[system_nr].add_chords_and_lyrics_line(line)
            system_line_nr += 1
            system_nr += 1
        elif line.line_type == LineType.Chords:
            system = System(system_nr)
            segment.add_system(system)
            system.add_chords_line(line)
            system_line_nr += 1

            if system_line_nr == len(segment.lines):
                break

            if segment.is_start_of_tab_block(system_line_nr):
                # Here is a tab block, but we ignore it as we already know the chords
                system_line_nr += 6

            # If the tab block is followed by max. 3 subsequent lyrics lines, add the lyrics to the system
            nr_of_subsequent_lyrics_lines = segment.length_of_lyrics_block(system_line_nr)
            for subsequent_lyric_i in range(0, nr_of_subsequent_lyrics_lines):
                system.add_lyrics_line(segment.lines[system_line_nr + subsequent_lyric_i])
            system_line_nr += nr_of_subsequent_lyrics_lines

            system_nr += 1
        elif segment.is_start_of_tab_block(system_line_nr):
            # Add new system
            system = System(system_nr)
            segment.systems.append(system)
            tab_block_str = [block_line.content for block_line in segment.lines[system_line_nr:system_line_nr + 6]]
            system.add_tab_block(tab_block_str)
            system_line_nr += 6
            # If the tab block is followed by max. 3 subsequent lyrics lines, add the lyrics to the system
            nr_of_subsequent_lyrics_lines = segment.length_of_lyrics_block(system_line_nr)
            for subsequent_lyric_i in range(0, nr_of_subsequent_lyrics_lines):
                system.add_lyrics_line(segment.lines[system_line_nr + subsequent_lyric_i])
            system_line_nr += nr_of_subsequent_lyrics_lines
            system_nr += 1
        else:
            system_line_nr += 1


def segment_line_list(line_list: List[Line]) -> List[Segment]:
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
        find_systems(segment)

    return result
