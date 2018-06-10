# -*- coding: utf-8 -*-
# import FileHandler
# from os import listdir
import re
from LineClasses import LineType, Line


def classify_lines(chord_sheet_path):
    """Classify all lines in chord_sheet_path to a Line"""
    result = []
    with open(chord_sheet_path, 'r') as chord_sheet:
        content = chord_sheet.readlines()
        line_nr = 0
        for line_content in content:
            line_content = line_content.rstrip()
            line_type = LineType(classify_line_type(line_content))
            line = Line(line_nr, line_content, line_type)
            result.append(line)
            line_nr += 1
    return result


def classify_line_type(line):
    """Classify line to a LineType"""
    if line.replace(' ', '') == '':
        return LineType.Empty
    if len(re.sub(r'[|]', ' ', line).split()) == len(find_chords(re.sub(r'[|]', ' ', line))):
        return LineType.Chords
    if re.match(r'.*tuning.*', line.lower()):
        return LineType.TuningDefinition
    if re.match(r'.*capo.*', line.lower()):
        return LineType.CapoChange
    if _is_structural_marker(line):
        return LineType.StructuralMarker
    if _contains_chord_definition(line):
        return LineType.ChordDefinition
    if _is_tab_line(line):
        return LineType.Tablature
    if _is_lyrics_line(line):
        return LineType.Lyrics
    if _is_chords_and_lyrics_line(line):
        return LineType.ChordsAndLyrics
    return LineType.Undefined


def find_chords(line):
    """Find all words looking like chords in this line and return them in a list"""
    words = line.split()
    result = []
    for word in words:
        if _word_is_chord(word):
            result.append(word)
    return result


def _is_structural_marker(line):
    """Check if this line is a structural marker"""
    line_lower_without_symbols = re.sub(r'[ :\[\];<>0-9]', '', line).lower()
    if line_lower_without_symbols in ['verse', 'chorus', 'intro', 'bridge', 'solo', 'instrumental', 'fine', 'coda',
                                      'outro', 'break', 'interlude']:
        return True
    if _contains_any_of(line.lower(), ['[verse]', '[chorus]', '[intro]', '[bridge]', '[solo]', '[instrumental]',
                                       '[fine]', '[coda]', '[outro]', '[break]', '[interlude]']):
        return True
    if len(re.findall(r'\[(verse|chorus|intro|bridge|solo|instrumental|fine|coda|outro|break|interlude).{,15}\]',
                      line.lower())) > 0:
        return True
    return False


def _contains_any_of(word, substring_list):
    """Check if word contains any of the substrings in list"""
    for substring in substring_list:
        if word.count(substring) > 0:
            return True
    return False


def _word_is_chord(word):
    """Check if word is a chord

    >>> _word_is_chord('Cmaj')
    True
    """
    word = word.lower()
    if len(word) >= 10:
        return False
    if word[0] not in 'abcdefgn':
        return False
    if re.match(r'.*[0-9]{4}.*', word):
        return False
    if len(word) == 1:
        return True
    if _contains_any_of(word, '!$%&*,.\':;<=>@[\\]^_{|}~'):
        return False
    word = word[1:]
    if re.match(r'.*[a-z]{3}.*', word) \
            and not _contains_any_of(word, ['min', 'add', 'aug', 'dim', 'maj', 'sus', 'flat']):
        return False
    return True


def _is_normal_word(word):
    """Check if this word is a normal word, which would be used in natural language (e.g. lyrics)"""
    if _word_is_chord(word):
        return False
    if len(word) > 2 and _contains_any_of(word[1:-1], '!#$%&()*+,-./:;<=>?@[\\]^_{|}~'):
        return False
    return True


def _contains_chord_definition(word):
    """Check if this word contains a chord definition"""
    if re.search(r'(^|.*\D)[0-9]{6}($|\D.*)', word):
        return True
    return False


def _is_tab_line(line):
    """Check if this line is a tablature line"""
    if re.match(r'\s*[eBGDAE]? {0,5}(\|\))? {0,5}[-0-9|b/hp ]{10,}.*', line) \
            and line.count('-') > line.count(' '):
        return True
    return False


def _is_lyrics_line(line):
    """Check if this line is a lyrics line"""
    if _contains_any_of(line, '\[\]=@'):
        return False
    if line.count('-') > 10:
        return False
    line2 = re.sub(r'[!\"#$%&\'()*+,-./:;<>?@\\^_`{|}~]', ' ', line)
    line2 = line2.lower()
    words = line2.split()
    if len(words) == 1 and _is_aaaaaah(words[0]):
        return True
    if len(words) < 2:
        return False
    nr_no_words = 0
    for word in words:
        if (not _is_normal_word(word)) and len(word) > 3:
            nr_no_words += 1
    if nr_no_words > 1:
        return False
    return True


def _is_aaaaaah(word):
    """Check if a word contains at least three of the same letters after each other and no non-letter characters

    >>> _is_aaaaaah('aaaaaaah')
    True
    >>> _is_aaaaaah('aah')
    False
    """
    previous_char = 'N'
    nr_same_char = 0
    for c in word:
        if c not in 'abcdefghijklmnopqrstuvwxyz':
            return False
        if c == previous_char:
            nr_same_char += 1
            if nr_same_char > 2 and previous_char != 'x':
                return True
        else:
            previous_char = c
            nr_same_char = 1
    return False


def _is_chords_and_lyrics_line(line):
    """Check if this line is a combined chords and lyrics line"""
    line2 = line.lower()
    optional_chords = re.findall(r'\[.{1,9}\]', line2)
    if len(optional_chords) == 0:
        return False
    for optional_chord in optional_chords:
        if not _word_is_chord(optional_chord[1:-1]):
            return False
    line2 = re.sub(r'\[.{1,9}\]', ' ', line2)
    return _is_lyrics_line(line2)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
