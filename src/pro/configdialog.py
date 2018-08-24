# -*- coding: utf-8 -*-

from PyQt5.Qt import *

from ..config import Config
from ..config import Filter
from ..config import Cross, CrossItem
from ..models import StrArrayListModel
from ..config import SafeDumper
from ..models import ArrayListModel
from ..models import convertToBuiltinType
from ..utils import and_concat

from .crossconfigdialog import CrossConfigDialog
from .filterconfigdialog import FilterConfigDialog
from .listdialog import ArraySelectDialog

from .ui_configdialog import Ui_ConfigDialog

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.ui = Ui_ConfigDialog()
        self.ui.setupUi(self)

        self.SOURCE_FILTER = self.tr('Excel (*.xlsx);;CSV (*.csv)')
        self.CONFIG_FILTER = self.tr('Config (*.yml)')

        self.BLANK_STR = self.tr('BLANK')
        self.TOTAL_STR = self.tr('TOTAL')

        self.config = Config()

        self.initUi()

    def initUi(self):
        # columns
        self.columnsModel = ArrayListModel(self)
        self.ui.listViewColumns.setModel(self.columnsModel)

        self.selectionModel = self.ui.listViewColumns.selectionModel()
        self.selectionModel.currentChanged.connect(self.columns_currentChanged)

        self.valuesModel = ArrayListModel(self)
        self.ui.listViewValues.setModel(self.valuesModel)

        # filters
        self.filtersModel = StrArrayListModel(self)
        self.ui.listViewFilters.setModel(self.filtersModel)

        # cross
        self.crossKeysModel = StrArrayListModel(self)
        self.ui.listViewCrossKeys.setModel(self.crossKeysModel)
        self.crossTargetsModel = StrArrayListModel(self)
        self.ui.listViewCrossTargets.setModel(self.crossTargetsModel)

        # selection models
        self.filtersSelection = self.ui.listViewFilters.selectionModel()
        self.crossKeysSelection = self.ui.listViewCrossKeys.selectionModel()
        self.crossTargetsSelection = self.ui.listViewCrossTargets.selectionModel()

        for selection in [self.filtersSelection, self.crossKeysSelection, self.crossTargetsSelection]:
            selection.selectionChanged.connect(self.selectionChanged)

        # enabled
        self.setupEnabled()

    def getConfig(self):
        # drop choice
        return Config(self.config)

    def setConfig(self, config):
        self.clearColumnsForm()
        self.config = Config(config)

        self.columnsModel.setArray(self.config.columnOrder)
        self.filtersModel.setArray(self.config.filters)
        self.crossKeysModel.setArray(self.config.cross.keys)
        self.crossTargetsModel.setArray(self.config.cross.targets)

    def clearColumnsForm(self):
        self.valuesModel.reset()
        self.ui.lineEditColumnsTitle.clear()
        self.ui.comboBoxColumnsType.setCurrentIndex(0)
        self.ui.checkBoxColumnsNoBlank.setChecked(False)

    def setupColumnsForm(self, column):
        conf = self.config.columns.get(column, {})
        self.valuesModel.setArray(list(conf.get('choice', [])))
        # title
        self.ui.lineEditColumnsTitle.setText(conf.get('title', ''))
        self.ui.lineEditColumnsTitle.setCursorPosition(0)
        # type
        column_type = conf.get('type', 0)
        if column_type not in [0, 1, 2]:
            column_type = 0
        self.ui.comboBoxColumnsType.setCurrentIndex(column_type)
        # noblank
        self.ui.checkBoxColumnsNoBlank.setChecked(conf.get('noblank', False))

    def updateColumnsConfig(self, key, data):
        current = self.ui.listViewColumns.currentIndex()
        if not current.isValid():
            self.valuesModel.setArray([])
            return
        value = self.columnsModel.array()[current.row()]
        column = convertToBuiltinType(value)
        columns = self.config.columns
        if column not in columns:
            columns[column] = {}
        columns[column][key] = data
        # bool (False) special case
        if isinstance(data, bool) and not data:
            del columns[column][key]
        self.config.columns = columns

    def setupEnabled(self):
        isReady = bool(self.config)
        # filters
        filterSelected = len(self.filtersSelection.selectedRows()) > 0
        self.ui.pushButtonFiltersNew.setEnabled(isReady)
        self.ui.pushButtonFiltersEdit.setEnabled(filterSelected)
        self.ui.pushButtonFiltersRemove.setEnabled(filterSelected)

        # cross keys
        crossKeySelected = len(self.crossKeysSelection.selectedRows()) > 0
        self.ui.pushButtonCrossKeysNew.setEnabled(isReady)
        self.ui.pushButtonCrossKeysEdit.setEnabled(crossKeySelected)
        self.ui.pushButtonCrossKeysRemove.setEnabled(crossKeySelected)
        self.ui.pushButtonCrossKeysFromList.setEnabled(isReady)

        # cross targets
        crossTargetSelected = len(self.crossTargetsSelection.selectedRows()) > 0
        self.ui.pushButtonCrossTargetsNew.setEnabled(isReady)
        self.ui.pushButtonCrossTargetsEdit.setEnabled(crossTargetSelected)
        self.ui.pushButtonCrossTargetsRemove.setEnabled(crossTargetSelected)
        self.ui.pushButtonCrossTargetsFromList.setEnabled(isReady)

    @pyqtSlot(QModelIndex, QModelIndex)
    def columns_currentChanged(self, current, previous):
        if not current.isValid():
            return
        value = self.columnsModel.array()[current.row()]
        key = convertToBuiltinType(value)
        self.setupColumnsForm(key)

    @pyqtSlot(str)
    def on_lineEditColumnsTitle_textChanged(self, text):
        self.updateColumnsConfig('title', str(text))

    @pyqtSlot(int)
    def on_comboBoxColumnsType_currentIndexChanged(self, index):
        self.updateColumnsConfig('type', index)

    @pyqtSlot(bool)
    def on_checkBoxColumnsNoBlank_clicked(self, checked):
        self.updateColumnsConfig('noblank', checked)

    @pyqtSlot()
    def on_pushButtonFiltersNew_clicked(self):
        columns = self.config.columns
        order = self.config.columnOrder
        dialog = FilterConfigDialog(columns, order, self)
        if dialog.exec_() == QDialog.Accepted:
            filter = Filter()
            filter.key = dialog.key()
            filter.type = dialog.type()
            filter.choices = dialog.choices()
            filter.targets = dialog.targets()
            self.config.filters.append(filter)
            self.filtersModel.setArray(self.config.filters)

    @pyqtSlot()
    def on_pushButtonFiltersEdit_clicked(self):
        current = self.ui.listViewFilters.currentIndex()
        if not current.isValid():
            return
        conf = self.config.filters[current.row()]
        columns = self.config.columns
        order = self.config.columnOrder
        dialog = FilterConfigDialog(columns, order, self)
        dialog.setKey(conf.key)
        dialog.setType(conf.type)
        dialog.setChoices(conf.choices)
        dialog.setTargets(conf.targets)
        if dialog.exec_() == QDialog.Accepted:
            filter = Filter()
            filter.key = dialog.key()
            filter.type = dialog.type()
            filter.choices = dialog.choices()
            filter.targets = dialog.targets()
            self.config.filters[current.row()] = filter
            self.filtersModel.setArray(self.config.filters)

    @pyqtSlot()
    def on_pushButtonFiltersRemove_clicked(self):
        current = self.ui.listViewFilters.currentIndex()
        if not current.isValid():
            return
        del self.config.filters[current.row()]
        self.filtersModel.setArray(self.config.filters)

    @pyqtSlot()
    def on_pushButtonCrossKeysNew_clicked(self):
        indexes = self.config.columnOrder
        dialog = CrossConfigDialog(indexes, self)
        if dialog.exec_() == QDialog.Accepted:
            item = self.createCrossItem(dialog)
            self.config.cross.setKey(item)
            self.crossKeysModel.setArray(self.config.cross.keys)

    @pyqtSlot()
    def on_pushButtonCrossKeysEdit_clicked(self):
        indexes = self.config.columnOrder
        dialog = CrossConfigDialog(indexes, self)
        idx = self.ui.listViewCrossKeys.currentIndex()
        item = self.config.cross.keys[idx.row()]
        dialog.setId(item.id)
        dialog.setName('' if item.name is None else item.name)
        if dialog.exec_() == QDialog.Accepted:
            newItem = self.createCrossItem(dialog)
            self.config.cross.keys[idx.row()] = newItem
            if item.id != newItem.id:
                self.config.cross.keys = [x for i,x in enumerate(self.config.cross.keys) if x.id != newItem.id or i == idx.row()]
            self.crossKeysModel.setArray(self.config.cross.keys)

    @pyqtSlot()
    def on_pushButtonCrossKeysRemove_clicked(self):
        idx = self.ui.listViewCrossKeys.currentIndex()
        del self.config.cross.keys[idx.row()]
        self.crossKeysModel.setArray(self.config.cross.keys)

    @pyqtSlot()
    def on_pushButtonCrossKeysFromList_clicked(self):
        indexes = self.config.columnOrder
        dialog = ArraySelectDialog(self)
        dialog.setArray(indexes)
        if dialog.exec_() == QDialog.Accepted:
            self.config.cross.keys = [CrossItem.by_id(indexes[x]) for x in dialog.indexes()]
            self.crossKeysModel.setArray(self.config.cross.keys)

    @pyqtSlot()
    def on_pushButtonCrossTargetsNew_clicked(self):
        indexes = self.config.columnOrder
        dialog = CrossConfigDialog(indexes, self)
        if dialog.exec_() == QDialog.Accepted:
            item = self.createCrossItem(dialog)
            self.config.cross.setTarget(item)
            self.crossTargetsModel.setArray(self.config.cross.targets)

    @pyqtSlot()
    def on_pushButtonCrossTargetsEdit_clicked(self):
        indexes = self.config.columnOrder
        dialog = CrossConfigDialog(indexes, self)
        idx = self.ui.listViewCrossTargets.currentIndex()
        item = self.config.cross.targets[idx.row()]
        dialog.setId(item.id)
        dialog.setName('' if item.name is None else item.name)
        if dialog.exec_() == QDialog.Accepted:
            newItem = self.createCrossItem(dialog)
            self.config.cross.targets[idx.row()] = newItem
            if item.id != newItem.id:
                self.config.cross.targets = [x for i,x in enumerate(self.config.cross.targets) if x.id != newItem.id or i == idx.row()]
            self.crossTargetsModel.setArray(self.config.cross.targets)

    @pyqtSlot()
    def on_pushButtonCrossTargetsRemove_clicked(self):
        idx = self.ui.listViewCrossTargets.currentIndex()
        del self.config.cross.targets[idx.row()]
        self.crossTargetsModel.setArray(self.config.cross.targets)

    @pyqtSlot()
    def on_pushButtonCrossTargetsFromList_clicked(self):
        indexes = self.config.columnOrder
        dialog = ArraySelectDialog(self)
        dialog.setArray(indexes)
        if dialog.exec_() == QDialog.Accepted:
            self.config.cross.targets = [CrossItem.by_id(indexes[x]) for x in dialog.indexes()]
            self.crossTargetsModel.setArray(self.config.cross.targets)

    def createCrossItem(self, dialog):
        id = dialog.id()
        name = dialog.name()
        item = None
        if name.isEmpty():
            item = CrossItem.by_id(id)
        else:
            item = CrossItem.by_id_with_name(id, str(name))
        return item

    @pyqtSlot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected, deselected):
        self.setupEnabled()
