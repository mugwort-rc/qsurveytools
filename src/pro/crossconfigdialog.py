# -*- coding: utf-8 -*-

from PyQt5.Qt import *

from models import ArrayListModel
from models import convertToBuiltinType

from .ui_crossconfigdialog import Ui_CrossConfigDialog

class CrossConfigDialog(QDialog):
    def __init__(self, columns, parent=None):
        super(CrossConfigDialog, self).__init__(parent)
        self.ui = Ui_CrossConfigDialog()
        self.ui.setupUi(self)

        self.columns = columns

        self.initUi()

    def initUi(self):
        self.columnModel = ArrayListModel(self)
        self.ui.listView.setModel(self.columnModel)

        # init model
        self.columnModel.setArray(self.columns)

        self.selection = self.ui.listView.selectionModel()

        self.selection.selectionChanged.connect(self.selectionChanged)

        self.setupEnabled()

    def setupEnabled(self):
        button = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        button.setEnabled(
            len(self.selection.selectedRows()) == 1
        )

    def name(self):
        return self.ui.lineEditName.text()

    def setName(self, name):
        self.ui.lineEditName.setText(name)

    def id(self):
        index = self.ui.listView.currentIndex().row()
        return self.columns[index]

    def setId(self, id):
        try:
            index = self.columns.index(id)
            idx = self.columnModel.index(index, 0)
            self.ui.listView.setCurrentIndex(idx)
            self.ui.listView.selectionModel().select(idx, QItemSelectionModel.Select)
        except ValueError:
            pass

    @pyqtSlot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected, deselected):
        self.setupEnabled()
