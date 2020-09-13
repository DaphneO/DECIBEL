from decibel.tab_chord_parser.line import Line
from decibel.tab_chord_parser.line_type import LineType
from decibel.tab_chord_parser.system import System


class Segment:
    def __init__(self, segment_nr: int):
        self.segment_nr = segment_nr
        self.lines = []
        self.structure_label = ''
        self.systems = []

    def __eq__(self, other):
        return self.segment_nr == other.segment_nr

    def add_system(self, system: System):
        self.systems.append(system)

    def add_line(self, line: Line):
        if line.line_type == LineType.StructuralMarker:
            self.structure_label = line.content
        else:
            self.lines.append(line)

    def is_start_of_tab_block(self, line_nr: int):
        if line_nr + 6 > len(self.lines):
            return False
        for j in range(0, 6):
            if self.lines[line_nr + j].line_type != LineType.Tablature:
                return False
        if line_nr + 6 < len(self.lines) and self.lines[line_nr + 6].line_type != LineType.Tablature:
            return False
        return True

    def length_of_lyrics_block(self, line_nr: int):
        length = 0
        for j in range(0, 3):
            if line_nr + j >= len(self.lines):
                return length
            if self.lines[line_nr + j].line_type == LineType.Lyrics:
                length += 1
            else:
                return length
        return length
