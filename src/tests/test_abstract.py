# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject, QVariant
from PyQt4.QtCore import QModelIndex

from .. import abstract

def test_fetched():
    obj = abstract.FetchObject(1000)
    # initial
    assert obj.fetched == 0
    assert obj.size == 1000
    # update
    obj.fetched = 100
    assert obj.fetched == 100
    assert obj.size == 1000
    # update to maximum
    obj.fetched = 1000
    assert obj.fetched == 1000
    assert obj.size == 1000
    # update to exceed maximum
    obj.fetched = 1200
    assert obj.fetched == 1000
    assert obj.size == 1000

def test_size():
    obj = abstract.FetchObject(1000)
    # initial
    assert obj.fetched == 0
    assert obj.size == 1000
    # update
    obj.fetched = 100
    assert obj.fetched == 100
    assert obj.size == 1000
    # reset size
    obj.size = 500
    assert obj.fetched == 0
    assert obj.size == 500

def test_canFetchMore():
    obj = abstract.FetchObject(1000)
    # initial
    assert obj.canFetchMore() == True
    # update
    obj.fetched = obj.size - 1
    assert obj.canFetchMore() == True
    # update to maximum
    obj.fetched = obj.size
    assert obj.canFetchMore() == False

def test_fetchMore():
    obj = abstract.FetchObject(500)
    # initial
    assert obj.fetched == 0
    assert obj.size == 500
    # 0 -> 250
    obj.fetchMore(250)
    assert obj.fetched == 250
    # 250 -> 500
    obj.fetchMore(250)
    assert obj.fetched == 500
    # check no change
    obj.fetchMore(250)
    assert obj.fetched == 500


class ListModel(abstract.AbstractListModel):
    def __init__(self, parent):
        super(ListModel, self).__init__(parent)
        self.items = []

    def setList(self, data):
        self.beginResetModel()
        self.items = data
        self.setRowSize(len(data))
        self.endResetModel()

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        return self.items[index.row()]

def test_AbstractListModel():
    model = ListModel(None)
    # initial
    assert model.rowCount() == 0
    assert model.columnCount() == 1
    assert model.canFetchMore() == False
    # set data
    model.setList(list("abcde"))
    assert model.canFetchMore() == True
    # fetch
    model.fetchMore()
    assert model.canFetchMore() == False
    assert model.rowCount() == 5
    # get data
    index = model.index(2, 0)
    assert model.data(index) == "c"


def run_test_for_table_or_item_model(model):
    # check initial status
    assert model.rowCount() == 0
    assert model.columnCount() == 0
    assert model.canFetchMore() == False
    # set data
    model.setData([
        list("abcde"),
        list("fghij"),
    ])
    assert model.canFetchMore() == True
    assert model.rowCount() == 0
    assert model.columnCount() == 0
    assert model.realRowCount() == 2
    assert model.realColumnCount() == 5
    # fetch
    model.fetchMore()
    assert model.canFetchMore() == False
    assert model.rowCount() == 2
    assert model.columnCount() == 5
    # get data
    index = model.index(1, 3)
    assert model.data(index) == "i"


class TableModel(abstract.AbstractTableModel):
    def __init__(self, parent):
        super(TableModel, self).__init__(parent)
        self.tableData = []

    def setData(self, data):
        self.beginResetModel()
        self.tableData = data
        self.setTableSize(len(data),
                          len(data[0]) if len(data) > 0 else 0)
        self.endResetModel()

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        # check index range
        if ( index.row() >= self.rowCount() or
             index.column() >= self.columnCount()):
            return QVariant()
        return self.tableData[index.row()][index.column()]

def test_AbstractTableModel():
    model = TableModel(None)
    run_test_for_table_or_item_model(model)


class TreeModel(abstract.AbstractItemModel):
    def __init__(self, parent):
        super(TreeModel, self).__init__(parent)
        self.treeData = []

    def setData(self, data):
        self.beginResetModel()
        self.treeData = data
        self.setItemSize(len(data),
                          len(data[0]) if len(data) > 0 else 0)
        self.endResetModel()

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        # check index range
        if ( index.row() >= self.rowCount() or
             index.column() >= self.columnCount()):
            return QVariant()
        return self.treeData[index.row()][index.column()]

def test_AbstractItemModel():
    model = TreeModel(None)
    run_test_for_table_or_item_model(model)
