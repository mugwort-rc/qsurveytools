# -*- coding: utf-8 -*-

from PyQt4.Qt import *

from .. import models
from .. import utils

from ui_conditiondialog import Ui_ConditionDialog


class ConditionDialog(QDialog):
    def __init__(self, config, parent=None):
        super(ConditionDialog, self).__init__(parent)
        self.ui = Ui_ConditionDialog()
        self.ui.setupUi(self)

        self.config = config
        self.targetsModel = models.StrArrayListModel(self)
        self.ui.comboBox.setModel(self.targetsModel)
        self.targetsModel.setArray(self.config.columnOrder)

        self.choicesModel = models.StrArrayListModel(self)
        self.ui.listView.setModel(self.choicesModel)
        self.choicesSelection = self.ui.listView.selectionModel()
        self.choicesSelection.selectionChanged.connect(self.initControlsEnabled)

        self.initControlsEnabled()

    def setupByCondition(self, condition):
        self.condition = condition
        if self.condition.key not in self.config.columnOrder:
            return

        self.ui.comboBox.setCurrentIndex(self.config.columnOrder.index(self.condition.key))
        self.on_comboBox_currentIndexChanged(self.condition.key)
        if self.condition.isIgnore():
            self.ui.radioButtonNG.setChecked(True)

        self.choicesSelection.clearSelection()
        for value in self.condition.values:
            if value <= 0 or value > len(self.config.columns[self.condition.key]):
                continue
            index = self.choicesModel.index(value-1, 0)
            if not index.isValid():
                continue
            self.choicesSelection.select(index, QItemSelectionModel.Select)

    def isChanged(self):
        return self.key() != self.condition.key or self.values() != self.condition.values or self.isIgnore() != self.condition.isIgnore()

    def key(self):
        return self.ui.comboBox.currentText()

    def values(self):
        selected = self.choicesSelection.selectedIndexes()
        return [index.row()+1 for index in selected]

    def isIgnore(self):
        return self.ui.radioButtonNG.isChecked()

    @pyqtSlot()
    def initControlsEnabled(self):
        while self.targetsModel.canFetchMore():
            self.targetsModel.fetchMore()
        while self.choicesModel.canFetchMore():
            self.choicesModel.fetchMore()

        index = self.ui.comboBox.currentIndex()
        if index == -1:
            self.setControlsEnabled(False)
            return
        selected = self.choicesSelection.selectedIndexes()
        if len(selected) == 0:
            self.setControlsEnabled(False)
            return
        self.setControlsEnabled(True)

    def setControlsEnabled(self, enabled):
        button = self.ui.buttonBox.button(QDialogButtonBox.Ok)
        button.setEnabled(enabled)

    @pyqtSlot(QString)
    def on_comboBox_currentIndexChanged(self, text):
        text = utils.text_type(text)
        if text not in self.config.columns:
            return
        choices = self.config.columns[text].get("choice", [])
        self.choicesModel.setArray(choices)
        self.initControlsEnabled()