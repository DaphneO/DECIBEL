from decibel.tab_chord_parser.line_type import LineType


class Line:
    def __init__(self, line_nr: int, content: str, line_type: LineType):
        """
        Creates a Line object

        :param line_nr: y-coordinate of the line
        :param content: Textual content of the line
        :param line_type: Line type (e.g. ChordDefinition, Lyrics, ...)
        """
        self.line_nr = line_nr
        self.content = content
        self.line_type = line_type
