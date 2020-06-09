from enum import Enum
from decibel.utils import chordtemplategenerator
from decibel.utils.musicobjects import PITCH_CLASSES
from decibel.music_objects.chord import Chord
from decibel.music_objects.interval import Interval
from decibel.music_objects.fingering import Fingering
from decibel.music_objects.pitch_class import PitchClass
import re
import scipy.spatial.distance as ssd


ALL_CHORDS_LIST = chordtemplategenerator.generate_chroma_all_chords()


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


PUBLIC_ENUMS = {
    'LineType': LineType
}


class Line:
    def __init__(self, line_nr, content, line_type):
        """
        Creates a Line object

        :param line_nr: y-coordinate of the line
        :param content: Textual content of the line
        :param line_type: Line type (e.g. ChordDefinition, Lyrics, ...)
        """
        self.line_nr = line_nr
        self.content = content
        self.line_type = line_type


class Segment:
    def __init__(self, segment_nr: int):
        self.segment_nr = segment_nr
        self.lines = []
        self.structure_label = ''
        self.systems = []

    def __eq__(self, other):
        return self.segment_nr == other.segment_nr

    def add_line(self, line: Line):
        if line.line_type == LineType.StructuralMarker:
            self.structure_label = line.content
        else:
            self.lines.append(line)

    def find_systems(self):
        system_nr = 0
        self_line_nr = 0
        while self_line_nr < len(self.lines):
            line = self.lines[self_line_nr]
            if line.line_type == LineType.ChordsAndLyrics:
                self.systems.append(System(system_nr))
                self.systems[system_nr].add_chords_and_lyrics_line(line)
                self_line_nr += 1
                system_nr += 1
            elif line.line_type == LineType.Chords:
                self.systems.append(System(system_nr))
                self.systems[system_nr].add_chords_line(line)
                self_line_nr += 1
                if self_line_nr == len(self.lines):
                    break
                if self.is_start_of_tab_block(self_line_nr):
                    # Here is a tab block, but we ignore it as we already know the chords
                    self_line_nr += 6
                # If the tab block is followed by max. 3 subsequent lyrics lines, add the lyrics to the system
                nr_of_subsequent_lyrics_lines = self.length_of_lyrics_block(self_line_nr)
                for subsequent_lyric_i in range(0, nr_of_subsequent_lyrics_lines):
                    self.systems[system_nr].add_lyrics_line(self.lines[self_line_nr + subsequent_lyric_i])
                self_line_nr += nr_of_subsequent_lyrics_lines
                system_nr += 1
            elif self.is_start_of_tab_block(self_line_nr):
                # Add new system
                self.systems.append(System(system_nr))
                tab_block_str = [block_line.content for block_line in self.lines[self_line_nr:self_line_nr + 6]]
                self.systems[system_nr].add_tab_block(tab_block_str)
                self_line_nr += 6
                # If the tab block is followed by max. 3 subsequent lyrics lines, add the lyrics to the system
                nr_of_subsequent_lyrics_lines = self.length_of_lyrics_block(self_line_nr)
                for subsequent_lyric_i in range(0, nr_of_subsequent_lyrics_lines):
                    self.systems[system_nr].add_lyrics_line(self.lines[self_line_nr + subsequent_lyric_i])
                self_line_nr += nr_of_subsequent_lyrics_lines
                system_nr += 1
            else:
                self_line_nr += 1

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


class System:
    def __init__(self, system_nr: int):
        self.system_nr = system_nr
        self.chords = []
        self.lyrics = []

    def add_lyrics_line(self, lyrics_line: Line):
        """
        Process the content of the lyrics line, adding each word to self.lyrics

        :param lyrics_line: Line object of the Lyrics type
        """
        assert lyrics_line.line_type == LineType.Lyrics
        self._add_lyrics_line_str(lyrics_line.content)

    def add_chords_line(self, chords_line: Line):
        """
        Process the content of the chord line, adding each (recognizable) chord to self.chords

        :param chords_line: Line object of the Chords type
        """
        assert chords_line.line_type == LineType.Chords
        chords_line_str = chords_line.content.replace('|', ' ')
        chord_index_strings = [(m.start(), m.group(0)) for m in re.finditer(r'\S+', chords_line_str)]
        for (chord_index, chord_string) in chord_index_strings:
            self._add_chord_from_str(chord_string, chord_index)

    def add_chords_and_lyrics_line(self, chords_and_lyrics_line: Line):
        """
        Process the content of the chords and lyrics line, adding each word and chord to self.words or self.lyrics

        :param chords_and_lyrics_line: Line object of the ChordsAndLyrics type
        """
        assert chords_and_lyrics_line.line_type == LineType.ChordsAndLyrics
        chords_and_lyrics_line_str = chords_and_lyrics_line.content

        # Find start and end indices of chords
        chord_indices = [(m.start(), m.end()) for m in re.finditer(r'\[.{1,10}\]', chords_and_lyrics_line_str)]

        # Replace the chord indices with spaces in order to find the lyrics
        chords_and_lyrics_line_without_chords = list(chords_and_lyrics_line_str)
        for (chord_start, chord_end) in chord_indices:
            for index in range(chord_start, chord_end):
                chords_and_lyrics_line_without_chords[index] = ' '
        chords_and_lyrics_line_str_without_chords = ''.join(chords_and_lyrics_line_without_chords)
        chords_and_lyrics_line_str_without_chords = \
            re.sub(r'[!\"#$%&()*+,-./:;<>?@\\^_`{|}~]', ' ', chords_and_lyrics_line_str_without_chords)
        self._add_lyrics_line_str(chords_and_lyrics_line_str_without_chords)

        # Now find the chords
        for (chord_start, chord_end) in chord_indices:
            chord_str = chords_and_lyrics_line_str[chord_start + 1:chord_end - 1]
            self._add_chord_from_str(chord_str, chord_end)

    def add_tab_block(self, tab_block_str):
        """
        Process the content of a tab block (6 subsequent lines of LineType Tablature), add chords to self.chords

        :param tab_block_str: Six subsequent Lines of the LineType Tablature
        """
        smallest_line_length = min([len(block_line_str) for block_line_str in tab_block_str])
        for chord_x in range(0, smallest_line_length):
            # Read all six strings together per x-coordinate
            finger_list = []
            for tab_block_line_str in reversed(tab_block_str):
                finger_list.append(tab_block_line_str[chord_x])
            fingers = ''.join(finger_list)

            if re.match(r'[x0-9]{6}', fingers) and fingers != 'xxxxxx':
                # A chord sounds at this x position!
                fingering = Fingering('1', fingers[0], fingers[1], fingers[2],
                                      fingers[3], fingers[4], fingers[5])
                fingering_chroma = fingering.get_extended_chroma_vector()

                # Find nearest chord from vocabulary
                smallest_distance = 2
                best_matching_chord_str = 'X'
                for [key_note, chord_type, chord_template] in ALL_CHORDS_LIST:
                    cosine_distance = ssd.cosine(fingering_chroma[:12], chord_template)
                    if cosine_distance < smallest_distance:
                        smallest_distance = cosine_distance
                        best_matching_chord_str = PITCH_CLASSES[key_note][0] + chord_type
                chord = Chord.from_common_tab_notation_string(best_matching_chord_str)

                # Fix bass note
                bass_note = PitchClass(fingering_chroma[12])
                bass_interval = Interval.from_pitch_class_distances(chord.root_note, bass_note)
                chord.bass_degree = bass_interval

                # Add to self.chords
                self.chords.append((chord_x, chord))

    def _add_lyrics_line_str(self, lyrics_line_str: str):
        """
        Take each word from lyrics_line_str and add it to self.lyrics

        :param lyrics_line_str: Lyrics line string
        """
        lyrics_line_str = lyrics_line_str.upper()
        lyrics_line_str = re.sub(r'[!\"#$%&()*+,-./:;<>?@\\^_`{|}~]', ' ', lyrics_line_str)
        new_lyrics = [(m.start(), m.group(0)) for m in re.finditer(r'\S+', lyrics_line_str)]
        self.lyrics = self.lyrics + new_lyrics

    def _add_chord_from_str(self, chord_str: str, chord_x: int):
        """
        Find the Chord from chord_str and add it to self.chords

        :param chord_str: String of the Chord
        :param chord_x: Integer index of the Chord
        """
        chord = Chord.from_common_tab_notation_string(chord_str)
        if chord is not None:
            self.chords.append((chord_x, chord))
