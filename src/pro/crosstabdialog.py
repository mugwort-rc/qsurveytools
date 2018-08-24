# -*- coding: utf-8 -*-

from PyQt5.Qt import *

from ..models import ArrayListModel

from .ui_crosstabdialog import Ui_CrosstabDialog

class CrosstabDialog(QDialog):
    def __init__(self, parent=None):
        super(CrosstabDialog, self).__init__(parent)
        self.ui = Ui_CrosstabDialog()
        self.ui.setupUi(self)

        self.initUi()

    def initUi(self):
        self.indexModel = SelectionLinkedArrayListModel(self)
        self.columnsModel = SelectionLinkedArrayListModel(self)
        self.ui.listViewIndex.setModel(self.indexModel)
        self.ui.listViewColumns.setModel(self.columnsModel)
        self.ui.listViewIndex.selectionModel().currentChanged.connect(self.listViewIndex_currentChanged)
        self.ui.listViewColumns.selectionModel().currentChanged.connect(self.listViewColumns_currentChanged)

    def setArray(self, array):
        self.indexModel.setArray(array)
        self.columnsModel.setArray(array)

    def index(self):
        return self.ui.listViewIndex.currentIndex().row()

    def columns(self):
        return self.ui.listViewColumns.currentIndex().row()

    @pyqtSlot(QModelIndex, QModelIndex)
    def listViewIndex_currentChanged(self, current, previous):
        self.indexModel.setCurrent(current.row())
        self.columnsModel.setReference(current.row())
        self.updateButtonState()

    @pyqtSlot(QModelIndex, QModelIndex)
    def listViewColumns_currentChanged(self, current, previous):
        self.indexModel.setReference(current.row())
        self.columnsModel.setCurrent(current.row())
        self.updateButtonState()

    def updateButtonState(self):
        btn = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        index = self.indexModel.current()
        columns = self.columnsModel.current()
        enabled = False
        if index >= 0 and columns >= 0 and index != columns:
            enabled = True
        btn.setEnabled(enabled)


class SelectionLinkedArrayListModel(ArrayListModel):
    def __init__(self, parent=None):
        super(SelectionLinkedArrayListModel, self).__init__(parent)
        self.curRow = -1
        self.refRow = -1

    def current(self):
        return self.curRow

    def setCurrent(self, row):
        self.curRow = row
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)

    def setReference(self, row):
        self.refRow = row
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)

    def data(self, index, role=Qt.DisplayRole):
        ret = super(SelectionLinkedArrayListModel, self).data(index, role)
        if role == Qt.BackgroundRole and index.row() == self.curRow:
            ret = Qt.lightGray
        return ret

    def flags(self, index):
        ret = super(SelectionLinkedArrayListModel, self).flags(index)
        if index.row() == self.refRow:
            ret ^= Qt.ItemIsSelectable
            ret ^= Qt.ItemIsEnabled
        return ret
