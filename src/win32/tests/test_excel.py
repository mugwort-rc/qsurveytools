# -*- coding: utf-8 -*-

from .. import excel


def test_com_range():
    assert list(excel.com_range(3)) == [1, 2, 3]
    assert list(excel.com_range(5)) == [1, 2, 3, 4, 5]


def run_test_byUsedRange(data):
    df = excel.byUsedRange(data)
    assert df.columns.values.tolist() == ['ID', 'A', 'B', 'C']
    assert df['ID'].values.tolist() == [1, 5]
    assert df.ix[0].values.tolist() == [1, 2, 3, 4]


def test_byUsedRange_list():
    data = [
        ['ID', 'A', 'B', 'C'],
        [1, 2, 3, 4],
        [5, 6, 7, 8],
    ]
    run_test_byUsedRange(data)


def test_byUsedRange_tuple():
    data = (
        ('ID', 'A', 'B', 'C'),
        (1, 2, 3, 4),
        (5, 6, 7, 8),
    )
    run_test_byUsedRange(data)