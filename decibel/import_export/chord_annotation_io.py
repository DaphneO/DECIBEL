from decibel.music_objects.chord import Chord
from decibel.music_objects.chord_annotation import ChordAnnotation
from decibel.music_objects.chord_annotation_item import ChordAnnotationItem


def import_chord_annotation(chord_annotation_file_path: str) -> ChordAnnotation:
    chord_annotation = ChordAnnotation()
    with open(chord_annotation_file_path, 'r') as read_file:
        chord_annotation_str_list = read_file.readlines()
        for chord_annotation_item_str in chord_annotation_str_list:
            chord_annotation.add_chord_annotation_item(_parse_chord_annotation_line(chord_annotation_item_str))
    return chord_annotation


def _parse_chord_annotation_line(chord_annotation_line: str) -> ChordAnnotationItem:
    chord_annotation_line_items = [x.strip() for x in chord_annotation_line.split()]
    start_time = float(chord_annotation_line_items[0])
    end_time = float(chord_annotation_line_items[1])
    chord = Chord.from_harte_chord_string(chord_annotation_line_items[2])
    return ChordAnnotationItem(start_time, end_time, chord)


def export_chord_annotation(chord_annotation: ChordAnnotation, write_path: str):
    with open(write_path, 'w') as write_file:
        for chord_annotation_item in chord_annotation.chord_annotation_items:
            chord_str = str(chord_annotation_item.chord)
            if chord_str == 'None':
                chord_str = 'N'
            write_file.write('{0} {1} {2}\n'.format(chord_str, str(chord_annotation_item.from_time),
                                                    str(chord_annotation_item.to_time)))
