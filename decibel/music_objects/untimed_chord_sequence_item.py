class UntimedChordSequenceItem:
    def __init__(self, line_nr: int, segment_nr: int, system_nr: int, chord_x: int, chord_str: str):
        self.line_nr = line_nr
        self.segment_nr = segment_nr
        self.system_nr = system_nr
        self.chord_x = chord_x
        self.chord_str = chord_str

    @classmethod
    def no_chord_symbol(cls, line_nr: int):
        return cls(line_nr, 0, 0, 0, 'N')

    @classmethod
    def from_str(cls, ucs_str: str):
        try:
            str_items = ucs_str.split(' ')
            line_nr = int(str_items[0])
            segment_nr = int(str_items[1])
            system_nr = int(str_items[2])
            chord_x = int(str_items[3])
            chord_str = str_items[4]
            return cls(line_nr, segment_nr, system_nr, chord_x, chord_str)
        except IndexError:
            raise Exception('The line {} did not have sufficient items (5 needed).'.format(ucs_str))
        except ValueError:
            raise Exception('The line {} is not in the correct format.'.format(ucs_str))

    def __str__(self):
        return ' '.join([str(self.line_nr), str(self.segment_nr), str(self.system_nr), str(self.chord_x),
                         self.chord_str])
