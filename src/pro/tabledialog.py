# -*- coding: utf-8 -*-

from PyQt5.Qt import *

from ..models import DataFrameTableModel
from ..models import SeriesTableModel

from .ui_tabledialog import Ui_TableDialog

class TableDialog(QDialog):
    def __init__(self, parent=None):
        super(TableDialog, self).__init__(parent)
        self.ui = Ui_TableDialog()
        self.ui.setupUi(self)
        self.selectionModel = None

        self.initUi()

    def initUi(self):
        raise NotImplementedError

    @pyqtSlot(QModelIndex, QModelIndex)
    def selectionChanged(self, selected, deselected):
        if self.selectionModel is None:
            return
        total = 0
        hasNum = False
        values = [index.data() for index in self.selectionModel.selectedIndexes()]
        for value in values:
            if isinstance(value, QVariant):
                if not value.isValid():
                    continue
                value,ok = value.toFloat()
                if not ok:
                    continue
            if isinstance(value, int) or isinstance(value, float):
                total += value
                hasNum = True
        values = set(values)
        total_str = self.tr('Total: %1 ').arg(total) if hasNum else ''
        count_str = self.tr('Count: %1 ').arg(len(values))
        size_str = self.tr('Size: %1 ').arg(len(selected.indexes()))
        self.ui.statusbar.showMessage(total_str+count_str+size_str)

class DataFrameDialog(TableDialog):
    def initUi(self):
        self.model = DataFrameTableModel(self)
        self.ui.tableView.setModel(self.model)
        self.selectionModel = self.ui.tableView.selectionModel()
        self.selectionModel.selectionChanged.connect(self.selectionChanged)

    def setDataFrame(self, frame):
        self.model.setDataFrame(frame)

    def dataFrame(self):
        return self.model.dataFrame()

class SeriesDialog(TableDialog):
    def initUi(self):
        self.model = SeriesTableModel(self)
        self.ui.tableView.setModel(self.model)
        self.selectionModel = self.ui.tableView.selectionModel()
        self.selectionModel.selectionChanged.connect(self.selectionChanged)

    def setSeries(self, series):
        self.model.setSeries(series)

    def series(self):
        return self.model.series()
