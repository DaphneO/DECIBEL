from decibel.music_objects.untimed_chord_sequence import UntimedChordSequence
from decibel.music_objects.untimed_chord_sequence_item import UntimedChordSequenceItem


def read_untimed_chord_sequence(ucs_path: str) -> UntimedChordSequence:
    untimed_chord_sequence = UntimedChordSequence()
    with open(ucs_path, 'r') as read_file:
        untimed_chord_sequence_str_list = read_file.readlines()[1:]
        for ucs_item_str in untimed_chord_sequence_str_list:
            untimed_chord_sequence.add_untimed_chord_sequence_item(
                UntimedChordSequenceItem.from_str(ucs_item_str.strip()))
    return untimed_chord_sequence


def write_untimed_chord_sequence(ucs_path: str, untimed_chord_sequence: UntimedChordSequence):
    with open(ucs_path, 'w') as write_file:
        write_file.write('LineNr SegmentNr SystemNr ChordX ChordStr\n')
        for ucs_item in untimed_chord_sequence.untimed_chord_sequence_item_items:
            write_file.write(str(ucs_item) + '\n')
