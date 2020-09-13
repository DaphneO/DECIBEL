from enum import Enum


class LineType(Enum):
    """
    Possible types of a line in a chord or tab file
    """
    ChordDefinition = 1
    CapoChange = 2
    TuningDefinition = 3
    StructuralMarker = 4
    StructureLayout = 5
    ChordsAndLyrics = 6
    Chords = 7
    Lyrics = 8
    Tablature = 9
    StrokePattern = 10
    Empty = 11
    Undefined = 12