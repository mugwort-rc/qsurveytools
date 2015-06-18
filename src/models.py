# -*- coding: utf-8 -*-

import numpy
import six

from PyQt4.Qt import *

import abstract

def convertToBuiltinType(data):
    if isinstance(data, numpy.int64):
        return long(data)
    elif isinstance(data, numpy.float64) or isinstance(data, float):
        if numpy.isnan(data):
            return QVariant()
        return float(data)
    else:
        return data


class DataFrameTableModel(abstract.AbstractTableModel):
    def __init__(self, parent=None):
        super(DataFrameTableModel, self).__init__(parent)
        self.frame = None
        self.row = None
        self.column = None

    def dataFrame(self):
        return self.frame

    def setDataFrame(self, frame):
        self.beginResetModel()
        self.frame = frame
        self.setTableSize(len(frame.index), len(frame.columns))
        self.endResetModel()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if self.frame is None:
            return QVariant()
        if orientation == Qt.Horizontal:
            return convertToBuiltinType(self.frame.columns[section])
        else:
            return convertToBuiltinType(self.frame.index[section])

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if self.frame is None:
            return QVariant()
        val = self.frame[self.frame.columns[index.column()]][self.frame.index[index.row()]]
        return convertToBuiltinType(val)

class SeriesTableModel(abstract.AbstractTableModel):
    def __init__(self, parent=None):
        super(SeriesTableModel, self).__init__(parent)
        self._series = None

    def series(self):
        return self._series

    def setSeries(self, series):
        self.beginResetModel()
        self._series = series
        self.setTableSize(len(self._series), 1)
        self.endResetModel()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if self._series is None:
            return QVariant()
        if orientation == Qt.Vertical:
            return convertToBuiltinType(self._series.index[section])

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if self._series is None:
            return QVariant()
        val = self._series[self._series.index[index.row()]]
        return convertToBuiltinType(val)

class ArrayListModel(abstract.AbstractListModel):
    def __init__(self, parent=None):
        super(ArrayListModel, self).__init__(parent)
        self._array = []

    def array(self):
        return self._array

    def setArray(self, array):
        self.beginResetModel()
        self._array = array
        self.setRowSize(len(self._array))
        self.endResetModel()

    def reset(self):
        self.setArray([])

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if self._array is None:
            return QVariant()
        return self._array[index.row()]

class ReprArrayListModel(ArrayListModel):

    REPR = repr

    def data(self, index, role=Qt.DisplayRole):
        if role not in [Qt.DisplayRole, Role.ObjectRole]:
            return QVariant()
        if self._array is None:
            return QVariant()
        val = self._array[index.row()]
        if role == Role.ObjectRole:
            return val
        return self.REPR(val)

class StrArrayListModel(ReprArrayListModel):
    REPR = six.text_type


class Role:
    ObjectRole = Qt.UserRole + 1
