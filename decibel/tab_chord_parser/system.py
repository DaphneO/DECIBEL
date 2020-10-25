import re

from scipy.spatial import distance as ssd

from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.fingering import Fingering
from decibel.music_objects.interval import Interval
from decibel.music_objects.pitch_class import PitchClass
from decibel.tab_chord_parser.line import Line
from decibel.tab_chord_parser.line_type import LineType


ALL_CHORDS_LIST: ChordVocabulary = ChordVocabulary.generate_chroma_all_chords()


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

    def add_tab_block(self, tab_block_str: [Line]):
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
                for chord_template in ALL_CHORDS_LIST.chord_templates:
                    cosine_distance = ssd.cosine(fingering_chroma[:12], chord_template.chroma_list)
                    if cosine_distance < smallest_distance:
                        smallest_distance = cosine_distance
                        best_matching_chord_str = str(PitchClass(chord_template.key))[0] + chord_template.mode
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
