# -*- coding: utf-8 -*-

from PyQt4.Qt import *

from models import ArrayListModel

from ui_filterconfigdialog import Ui_FilterConfigDialog

class FilterConfigDialog(QDialog):
    def __init__(self, columns, keys, parent=None):
        super(FilterConfigDialog, self).__init__(parent)
        self.ui = Ui_FilterConfigDialog()
        self.ui.setupUi(self)

        self.columns = columns
        self.keys = keys

        self.initUi()

    def initUi(self):
        self.keyModel = ArrayListModel(self)
        self.ui.listView.setModel(self.keyModel)
        self.choiceModel = ArrayListModel(self)
        self.ui.listViewChoice.setModel(self.choiceModel)
        self.targetModel = TargetListModel(self)
        self.ui.listViewTarget.setModel(self.targetModel)

        # init model
        self.keyModel.setArray(self.keys)
        self.targetModel.setArray(self.keys)

        self.selection = self.ui.listView.selectionModel()
        self.choiceSelection = self.ui.listViewChoice.selectionModel()
        self.targetSelection = self.ui.listViewTarget.selectionModel()

        self.selection.currentChanged.connect(self.listView_currentChanged)

        for selection in [self.selection, self.choiceSelection, self.targetSelection]:
            selection.selectionChanged.connect(self.selectionChanged)

        self.setupEnabled()

    def setupEnabled(self):
        button = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        button.setEnabled(
            len(self.selection.selectedRows()) == 1 and
            len(self.choiceSelection.selectedRows()) > 0 and
            len(self.targetSelection.selectedRows()) > 0
        )

    def key(self):
        index = self.ui.listView.currentIndex().row()
        return self.keys[index]

    def setKey(self, key):
        try:
            index = self.keys.index(key)
            self.ui.listView.setCurrentIndex(self.keyModel.index(index, 0))
        except IndexError:
            pass

    def type(self):
        if self.isPickup():
            return 'pickup'
        elif self.isIgnore():
            return 'ignore'

    def setType(self, type):
        if type == 'pickup':
            self.setPickup()
        elif type == 'ignore':
            self.setIgnore()

    def isPickup(self):
        return self.ui.radioButtonPickup.isChecked()

    def setPickup(self, check=True):
        self.ui.radioButtonPickup.setChecked(check)

    def isIgnore(self):
        return self.ui.radioButtonIgnore.isChecked()

    def setIgnore(self, check=True):
        self.ui.radioButtonIgnore.setChecked(check)

    def choices(self):
        result = []
        for index in self.ui.listViewChoice.selectedIndexes():
            result.append(index.row()+1)
        return sorted(result)

    def setChoices(self, choices):
        self.ui.listViewChoice.clearSelection()
        for choice in choices:
            index = self.choiceModel.index(choice-1, 0)
            if not index.isValid():
                continue
            self.ui.listViewChoice.selectionModel().select(index, QItemSelectionModel.Select)

    def targets(self):
        result = []
        for index in self.ui.listViewTarget.selectedIndexes():
            result.append(self.keys[index.row()])
        return result

    def setTargets(self, targets):
        self.ui.listViewTarget.clearSelection()
        for target in targets:
            if target not in self.keys:
                continue
            index = self.targetModel.index(self.keys.index(target), 0)
            self.ui.listViewTarget.selectionModel().select(index, QItemSelectionModel.Select)

    @pyqtSlot(QModelIndex, QModelIndex)
    def listView_currentChanged(self, current, previous):
        if not current.isValid():
            return
        # choice
        col = self.keys[current.row()]
        if col in self.columns:
            self.choiceModel.setArray(self.columns[col].get('choice', []))
        else:
            self.choiceModel.reset()
        # target
        self.targetModel.setCurrent(current.row())

    @pyqtSlot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected, deselected):
        self.setupEnabled()


class TargetListModel(ArrayListModel):
    def __init__(self, parent=None):
        super(TargetListModel, self).__init__(parent)
        self.curRow = -1

    def current(self):
        return self.curRow

    def setCurrent(self, row):
        self.curRow = row
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)

    def flags(self, index):
        ret = super(TargetListModel, self).flags(index)
        if index.row() == self.curRow:
            ret ^= Qt.ItemIsSelectable
            ret ^= Qt.ItemIsEnabled
        return ret
