# -*- coding: utf-8 -*-

from PyQt4.Qt import *

from models import ArrayListModel

from ui_listdialog import Ui_ListDialog

class ListDialog(QDialog):
    def __init__(self, parent):
        super(ListDialog, self).__init__(parent)
        self.ui = Ui_ListDialog()
        self.ui.setupUi(self)

        self.initUi()

    def initUi(self):
        pass

class ArrayListDialog(ListDialog):
    def initUi(self):
        self.model = ArrayListModel(self)
        self.ui.listView.setModel(self.model)

    def setArray(self, array):
        self.model.setArray(array)

    def array(self):
        return self.model.array()

class ArraySelectDialog(ArrayListDialog):
    def index(self):
        return self.ui.listView.currentIndex().row()

    def indexes(self):
        return sorted([x.row() for x in self.ui.listView.selectionModel().selectedIndexes()])
