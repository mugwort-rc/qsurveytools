# -*- coding: utf-8 -*-

from .. import utils


def test_unique_list():
    assert utils.unique_list([1, 1, 2, 2, 3, 3, 4]) == [1, 2, 3, 4]
    assert utils.unique_list([2, 1, 1, 2, 3, 4, 3]) == [2, 1, 3, 4]
