# -*- coding: utf-8 -*-

import pandas

import pytest
from pytestqt.qt_compat import QT_API

from .. import models


frame = pandas.DataFrame([
        [1, 2, 3],
        ["x", "y", "z"],
        [1.1, 2.2, 3.3],
    ], columns=["a", "b", "c"])

series = pandas.Series([
    1,
    "a",
    1.1,
], index=["x", "y", "z"])

array = [
    1,
    "a",
    1.1,
]

class ReprObject(object):
    def __init__(self, value, repr):
        self.value = value
        self.repr = repr

    def __unicode__(self):
        return self.value

    def __repr__(self):
        return self.repr

objects = [
    ReprObject("a", "x"),
    ReprObject("b", "y"),
    ReprObject("c", "z"),
]


def gen_dataframemodel():
    model = models.DataFrameTableModel()
    model.setDataFrame(frame)
    return model

def gen_seriesmodel():
    model = models.SeriesTableModel()
    model.setSeries(series)
    return model

def gen_arraymodel():
    model = models.ArrayListModel()
    model.setArray(array)
    return model

def gen_reprmodel():
    model = models.ReprArrayListModel()
    model.setArray(objects)
    return model

def gen_strmodel():
    model = models.StrArrayListModel()
    model.setArray(objects)
    return model

def expand_model(model):
    while model.canFetchMore():
        model.fetchMore()
    return model


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_dataframemodel(qapp):
    model = gen_dataframemodel()
    assert model.dataFrame().equals(frame)
    assert model.canFetchMore() == True
    expand_model(model)
    assert model.canFetchMore() == False
    assert model.rowCount() == 3
    assert model.columnCount() == 3


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_dataframemodel_data(qapp):
    model = gen_dataframemodel()
    expand_model(model)
    ret = model.data(model.index(0, 0))
    assert isinstance(ret, int)
    assert ret == 1
    ret = model.data(model.index(1, 1))
    assert ret == "y"
    ret = model.data(model.index(2, 2))
    assert isinstance(ret, float)
    assert ret == 3.3

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_dataframemodel_headerData(qapp):
    model = gen_dataframemodel()
    expand_model(model)
    from PyQt4.QtCore import Qt
    assert model.headerData(0, Qt.Horizontal) == "a"


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_seriesmodel(qapp):
    model = gen_seriesmodel()
    assert model.series().equals(series)
    assert model.canFetchMore() == True
    expand_model(model)
    assert model.canFetchMore() == False
    assert model.rowCount() == 3
    assert model.columnCount() == 1

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_seriesmodel_data(qapp):
    model = gen_seriesmodel()
    expand_model(model)
    ret = model.data(model.index(0, 0))
    assert isinstance(ret, int)
    assert ret == 1
    ret = model.data(model.index(1, 0))
    assert ret == "a"
    ret = model.data(model.index(2, 0))
    assert isinstance(ret, float)
    assert ret == 1.1

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_seriesmodel_headerData(qapp):
    model = gen_seriesmodel()
    expand_model(model)
    from PyQt4.QtCore import Qt
    assert model.headerData(0, Qt.Vertical) == "x"


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_arraymodel(qapp):
    model = gen_arraymodel()
    assert model.array() == array
    assert model.canFetchMore() == True
    expand_model(model)
    assert model.canFetchMore() == False
    assert model.rowCount() == 3
    assert model.columnCount() == 1

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_arraymodel_data(qapp):
    model = gen_arraymodel()
    expand_model(model)
    ret = model.data(model.index(0, 0))
    assert isinstance(ret, int)
    assert ret == 1
    ret = model.data(model.index(1, 0))
    assert ret == "a"
    ret = model.data(model.index(2, 0))
    assert isinstance(ret, float)
    assert ret == 1.1

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_arraymodel_data(qapp):
    model = gen_arraymodel()
    model.reset()
    assert model.array() != array
    assert model.array() == []


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_reprmodel(qapp):
    model = gen_reprmodel()
    assert model.array() == objects
    assert model.canFetchMore() == True
    expand_model(model)
    assert model.canFetchMore() == False
    assert model.rowCount() == 3
    assert model.columnCount() == 1

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_reprmodel_data(qapp):
    model = gen_reprmodel()
    expand_model(model)
    assert model.data(model.index(0, 0)) == "x"
    assert model.data(model.index(1, 0)) == "y"
    assert model.data(model.index(2, 0)) == "z"
    assert model.data(model.index(0, 0), models.Role.ObjectRole) == objects[0]
    assert model.data(model.index(1, 0), models.Role.ObjectRole) == objects[1]
    assert model.data(model.index(2, 0), models.Role.ObjectRole) == objects[2]


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_strmodel(qapp):
    model = gen_strmodel()
    assert model.array() == objects
    assert model.canFetchMore() == True
    expand_model(model)
    assert model.canFetchMore() == False
    assert model.rowCount() == 3
    assert model.columnCount() == 1

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_strmodel_data(qapp):
    model = gen_strmodel()
    expand_model(model)
    assert model.data(model.index(0, 0)) == "a"
    assert model.data(model.index(1, 0)) == "b"
    assert model.data(model.index(2, 0)) == "c"
    assert model.data(model.index(0, 0), models.Role.ObjectRole) == objects[0]
    assert model.data(model.index(1, 0), models.Role.ObjectRole) == objects[1]
    assert model.data(model.index(2, 0), models.Role.ObjectRole) == objects[2]
