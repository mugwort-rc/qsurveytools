# -*- coding: utf-8 -*-

import pandas

from .. import utils


def test_unique_list():
    assert utils.unique_list([1, 1, 2, 2, 3, 3, 4]) == [1, 2, 3, 4]
    assert utils.unique_list([2, 1, 1, 2, 3, 4, 3]) == [2, 1, 3, 4]


def test_int_cast():
    assert utils.int_cast(1) == 1
    assert utils.int_cast("2") == 2
    assert utils.int_cast("3.0") == "3.0"
    assert utils.int_cast(None) == None
    assert utils.int_cast("a") == "a"


def test_round_cast():
    assert utils.round_cast(1.0) == 1
    assert utils.round_cast(1.1) == 1.1
    assert utils.round_cast(1) == 1
    assert utils.round_cast("1.0") == "1.0"


def test_expand_multiple():
    expanded = utils.expand_multiple(pandas.Series([
        "1,2,3",
        4,
        None,
        "3,3",
    ]))
    assert isinstance(expanded, pandas.DataFrame)
    assert len(expanded.columns) == 3
    assert len(expanded.index) == 4
    expanded = expanded.fillna(-1)
    assert expanded.ix[0].values.tolist() == [1, 2, 3]
    assert expanded.ix[1].values.tolist() == [4, -1, -1]
    assert expanded.ix[2].values.tolist() == [-1, -1, -1]
    assert expanded.ix[3].values.tolist() == [3, -1, -1]

    expanded = utils.expand_multiple(pandas.Series([]))
    assert isinstance(expanded, pandas.DataFrame)
    assert len(expanded) == 0


def test_expand_multiple_bool():
    expanded = utils.expand_multiple_bool(pandas.Series([
        "1,2,3",
        4,
        None,
        "3,3",
    ]))
    assert isinstance(expanded, pandas.DataFrame)
    assert len(expanded.columns) == 4
    assert len(expanded.index) == 4
    assert expanded.ix[0].values.tolist() == [True, True, True, False]
    assert expanded.ix[1].values.tolist() == [False, False, False, True]
    assert expanded.ix[2].values.tolist() == [False, False, False, False]
    assert expanded.ix[3].values.tolist() == [False, False, True, False]

    expanded = utils.expand_multiple_bool(pandas.Series([]))
    assert isinstance(expanded, pandas.DataFrame)
    assert len(expanded) == 0

    
def test_expand_base():
    expanded = utils.expand_base(pandas.Series([
        "1,2,3",
        4,
        None,
        "3,3",
    ]))
    assert isinstance(expanded, pandas.Series)
    assert len(expanded.index) == 3
    expanded = expanded.fillna(-1)
    assert expanded[0] == set([1, 2, 3])
    assert expanded[1] == set([4])
    assert expanded[3] == set([3])

    expanded = utils.expand_base(pandas.Series([]))
    assert isinstance(expanded, pandas.Series)
    assert len(expanded) == 0

