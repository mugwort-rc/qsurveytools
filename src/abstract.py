# -*- coding: utf-8 -*-

from PyQt5.QtCore import QAbstractItemModel, QAbstractListModel, QAbstractTableModel
from PyQt5.QtCore import QModelIndex

class FetchObject(object):
    """
    FetchObject
    ===========
    implementation of fetchMore
    """

    # size per fetch
    FETCHSIZE = 250

    def __init__(self, size):
        """
        :type size: int
        :param size: maximum size
        """
        self.size = size

    def canFetchMore(self):
        """
        :rtype: bool
        :return: status of can fetch more
        """
        return self.fetched < self.size

    def fetchSize(self, more=FETCHSIZE):
        """
        :type more: int
        :param more: size of fetch
        :rtype: int
        :return: size of after fetched
        """
        remainder = self.size - self.fetched
        return min(more, remainder)

    def fetchMore(self, more=FETCHSIZE):
        """
        :type more: int
        :param more: size of fetch
        """
        itemsToFetch = self.fetchSize(more)
        self.fetched += itemsToFetch

    @property
    def fetched(self):
        """
        :rtype: int
        :return: fetched size
        """
        return self._fetched
    @fetched.setter
    def fetched(self, fetched):
        """
        :type fetched: int
        :param fetched: fetched size
        """
        self._fetched = min(fetched, self.size)

    @property
    def size(self):
        """
        :rtype: int
        :return: maximum size
        """
        return self._size
    @size.setter
    def size(self, size):
        """
        :type size: int
        :param size: maximum size
        """
        self._size = size
        self.fetched = 0

class AbstractListModel(QAbstractListModel):
    """
    AbstractListModel
    =================

    for QListView

    Usage::

        class ListModel(AbstractListModel):
            def setList(self, items):
                self.beginResetModel()
                self.items = items
                self.setRowSize(len(items))
                self.endResetModel()

            def data(self, index=QModelIndex(), role=Qt.DisplayRole):
                ...
    """

    def __init__(self, parent):
        """
        :type parent: QObject
        :param parent: parent QObject
        """
        super(AbstractListModel, self).__init__(parent)
        self.row = None

    def canFetchMore(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: bool
        :return: status of can fetch more
        """
        # check if source has been set
        if self.row is None:
            return False
        return self.row.canFetchMore()

    def fetchMore(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        """
        # check if source has been set
        if self.row is None:
            return
        itemsToFetch = self.row.fetchSize()
        self.beginInsertRows(QModelIndex(),
                             self.row.fetched,
                             self.row.fetched + itemsToFetch - 1)
        self.row.fetchMore(itemsToFetch)
        self.endInsertRows()

    def columnCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of column
        """
        return 1

    def rowCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of items
        """
        if self.row is None:
            return 0
        return self.row.fetched

    def setRowSize(self, size):
        """
        .. note::
           must be call between beginResetModel() and endResetModel()

        :type size: int
        :param size: size of items
        """
        self.row = FetchObject(size)

    def resetFetch(self):
        """
        .. note::
           must be call between beginResetModel() and endResetModel()
        """
        self.row = None

class AbstractTableModel(QAbstractTableModel):
    """
    AbstractTableModel
    ==================

    for QTableView

    Usage::

        class TableModel(AbstractTableModel):
            def setData(self, data):
                self.beginResetModel()
                self.tableData = data
                self.setTableSize(len(data),
                                  len(data[0]) if len(data) > 0 else 0)
                self.endResetModel()

            def data(self, index=QModelIndex(), role=Qt.DisplayRole):
                ...
    """

    def __init__(self, parent):
        """
        :type parent: QObject
        :param parent: parent QObject
        """
        super(AbstractTableModel, self).__init__(parent)
        self.row = None
        self.column = None

    def canFetchMore(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: bool
        :return: status of can fetch more
        """
        # check if source has been set
        if self.row is None or self.column is None:
            return False
        return self.row.canFetchMore() or self.column.canFetchMore()

    def fetchMore(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        """
        # check if source has been set
        if self.row is None or self.column is None:
            return
        # row side
        if self.row.canFetchMore():
            itemsToFetch = self.row.fetchSize()
            self.beginInsertRows(QModelIndex(),
                                 self.row.fetched,
                                 self.row.fetched + itemsToFetch - 1)
            self.row.fetchMore(itemsToFetch)
            self.endInsertRows()
        # column side
        if self.column.canFetchMore():
            itemsToFetch = self.column.fetchSize()
            self.beginInsertColumns(QModelIndex(),
                                    self.column.fetched,
                                    self.column.fetched + itemsToFetch - 1)
            self.column.fetchMore(itemsToFetch)
            self.endInsertColumns()

    def columnCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of column
        """
        if self.column is None:
            return 0
        return self.column.fetched

    def rowCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of row
        """
        if self.row is None:
            return 0
        return self.row.fetched

    def realColumnCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of maximum column
        """
        if self.column is None:
            return 0
        return self.column.size

    def realRowCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of maximum row
        """
        if self.row is None:
            return 0
        return self.row.size

    def setTableSize(self, row, column):
        """
        .. note::
           must be call between beginResetModel() and endResetModel()
        :type row: int
        :param row: size of maximum row
        :type column: int
        :param column: size of maximum column
        """
        self.row = FetchObject(row)
        self.column = FetchObject(column)

    def resetFetch(self):
        """
        .. note::
           must be call between beginResetModel() and endResetModel()
        """
        self.row = None
        self.column = None

class AbstractItemModel(QAbstractItemModel):
    """
    AbstractItemModel
    =================

    for QTreeView, QListView etc

    Usage::

        class TreeModel(AbstractItemModel):
            def setData(self, data):
                self.beginResetModel()
                self.treeData = data
                self.setItemSize(len(items),
                                 len(items[0]) if len(items) > 0 else 0)
                self.endResetModel()

            def data(self, index=QModelIndex(), role=Qt.DisplayRole):
                ...
    """

    def __init__(self, parent):
        """
        :type parent: QObject
        :param parent: parent QObject
        """
        super(AbstractItemModel, self).__init__(parent)
        self.row = None
        self.column = None

    def canFetchMore(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: bool
        :return: status of can fetch more
        """
        # check if source has been set
        if self.row is None or self.column is None:
            return False
        return self.row.canFetchMore() or self.column.canFetchMore()

    def fetchMore(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        """
        # check if source has been set
        if self.row is None or self.column is None:
            return
        # row side
        if self.row.canFetchMore():
            itemsToFetch = self.row.fetchSize()
            self.beginInsertRows(QModelIndex(),
                                 self.row.fetched,
                                 self.row.fetched + itemsToFetch - 1)
            self.row.fetchMore(itemsToFetch)
            self.endInsertRows()
        # column side
        if self.column.canFetchMore():
            itemsToFetch = self.column.fetchSize()
            self.beginInsertColumns(QModelIndex(),
                                    self.column.fetched,
                                    self.column.fetched + itemsToFetch - 1)
            self.column.fetchMore(itemsToFetch)
            self.endInsertColumns()

    def index(self, row, column, parent=QModelIndex()):
        if self.hasIndex(row, column, parent):
            return self.createIndex(row, column)
        return QModelIndex()

    def columnCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of column
        """
        if self.column is None:
            return 0
        return self.column.fetched

    def rowCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of row
        """
        if self.row is None:
            return 0
        return self.row.fetched

    def realColumnCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of maximum column
        """
        if self.column is None:
            return 0
        return self.column.size

    def realRowCount(self, parent=QModelIndex()):
        """
        :type parent: QModelIndex
        :param parent: parent index
        :rtype: int
        :return: size of maximum row
        """
        if self.row is None:
            return 0
        return self.row.size

    def setItemSize(self, row, column):
        """
        .. note::
           must be call between beginResetModel() and endResetModel()
        :type row: int
        :param row: size of maximum row
        :type column: int
        :param column: size of maximum column
        """
        self.row = FetchObject(row)
        self.column = FetchObject(column)

    def resetFetch(self):
        """
        .. note::
           must be call between beginResetModel() and endResetModel()
        """
        self.row = None
        self.column = None

__all__ = [
    "AbstractListModel", "AbstractTableModel", "AbstractItemModel",
    "FetchObject",
]
