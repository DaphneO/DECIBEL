def find_item(list_containing_list, item):
    """
    Find the index of the list that contains the item

    :param list_containing_list: List of lists; one of them must contain the item
    :param item: The item we are looking for
    :return: Index of the item in the outer list

    >>> find_item([[1,2,3],[4,5,6]],5)
    1
    """
    for _list in list_containing_list:
        if item in _list:
            return list_containing_list.index(_list)
    return None
