# -*- coding: utf-8 -*-

PITCH_CLASSES = ['C', 'C#', 'D', 'Eb', 'E', 'F',
                 'F#', 'G', 'G#', 'A', 'Bb', 'B']

HARTE_PITCH_CLASSES = [
    ['B#', 'C', 'Dbb'],
    ['B##', 'C#', 'Db'],
    ['C##', 'D', 'Ebb'],
    ['D#', 'Eb', 'Fbb'],
    ['D##', 'E', 'Fb'],
    ['E#', 'F', 'Gbb'],
    ['E##', 'F#', 'Gb'],
    ['F##', 'G', 'Abb'],
    ['G#', 'Ab'],
    ['G##', 'A', 'Bbb'],
    ['A#', 'Bb', 'Cbb'],
    ['A##', 'B', 'Cb']
]

INTERVALS = ['1', 'b2', '2', 'b3', '3', '4', '#4', '5', 'b6', '6', 'b7', '7', '8',
             'b9', '9', 'b10', '10', '11', 'b12', '12', 'b13', '13', '#13']

HARTE_INTERVALS = [
    ['1', 'bb2'], ['#1', 'b2'], ['2', 'bb3'],
    ['#2', 'b3'], ['3', 'b4'], ['#3', '4'],
    ['#4', 'b5'], ['5', 'bb6'], ['#5', 'b6'],
    ['6', 'bb7'], ['#6', 'b7'], ['7', 'b8'],
    ['#7', '8', 'bb9'], ['#8', 'b9'], ['9', 'bb10'],
    ['#9', 'b10'], ['10', 'b11'], ['#10', '11'],
    ['#11', 'b12'], ['12', 'bb13'], ['#12', 'b13'],
    ['13'], ['#13']
]


def _find_item(list_containing_list, item):
    """
    Find the index of the list that contains the item

    :param list_containing_list: List of lists; one of them must contain the item
    :param item: The item we are looking for
    :return: Index of the item in the outer list

    >>> _find_item([[1,2,3],[4,5,6]],5)
    1
    >>> _find_item(HARTE_INTERVALS, 'b13')
    20
    """
    for _list in list_containing_list:
        if item in _list:
            return list_containing_list.index(_list)
    return None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
