# -*- coding: utf-8 -*-

from PyQt4.Qt import *

import win32com.client
from pywintypes import com_error
import constants

from .. import config
from .. import cursor
from .. import models
import frame

from conditiondialog import ConditionDialog

from ui_mainwindow import Ui_MainWindow

class Mode:
    Default = 0
    NotOpen = 1
    Incorrect = 2
    Editing = 3

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.currentHash = None
        self.XL = None
        self.config = None
        self.filterController = None

        self.targetsLastSelect = None
        self.targetsLastSelectText = None

        self.initUi()

    def initUi(self):
        self.installEventFilter(self)

        self.targetsModel = models.StrArrayListModel(self)
        self.conditionsModel = FilterArrayListModel(self)
        self.ui.listViewTarget.setModel(self.targetsModel)
        self.ui.listViewCondition.setModel(self.conditionsModel)

        self.targetsSelection = self.ui.listViewTarget.selectionModel()
        self.conditionsSelection = self.ui.listViewCondition.selectionModel()
        self.targetsSelection.selectionChanged.connect(self.on_targetsSelectionChanged)
        self.conditionsSelection.selectionChanged.connect(self.on_conditionsSelectionChanged)

        self.controls = [
            self.ui.listViewTarget,
            self.ui.listViewCondition,
        ]
        self.editControls = [
            self.ui.pushButtonEdit,
            self.ui.pushButtonRemove,
        ]
        self.setControlsEnabled(False)
        self.setConditionControlsEnabled(False)

    def eventFilter(self, object, event):
        if event.type() == QEvent.WindowActivate:
            self.checkCurrentSheet()
            return True
        return False

    def activeSheet(self):
        if self.XL is None:
            with cursor.BusyCursor(self):
                self.XL = win32com.client.Dispatch('Excel.Application')
        try:
            result = self.XL.ActiveSheet
            return result
        except (AttributeError, com_error) as e:
            self.setMode(Mode.Editing)
            return

    def checkCurrentSheet(self):
        sheet = self.activeSheet()
        if sheet is None:
            self.setMode(Mode.NotOpen)
            return
        hashed = hash(sheet.UsedRange())
        if hashed != self.currentHash:
            self.reset()

    def reset(self):
        sheet = self.activeSheet()
        if sheet is None:
            return
        data = sheet.UsedRange()
        self.currentHash = hash(data)
        # empty, only A1, header length, header ID
        if ( data is None or
              not isinstance(data, tuple) or
              len(data) < 8 or
              data[0][0] != 'ID' ):
            self.setMode(Mode.Incorrect)
            return
        with cursor.BusyCursor(self):
            self.showMessage(self.tr("loading..."))
            df = frame.byUsedRange(data)
            try:
                conf = config.makeConfigByDataFrame(df)
            except:
                self.setMode(Mode.Incorrect)
                return
            self.setUsedRange(data)
            self.setConfig(conf)
            self.setMode(Mode.Default)

    def setUsedRange(self, used):
        self.idMap = {}
        for i,x in enumerate(used[0], 1):
            if x in self.idMap:
                # TODO: warning id collision
                continue
            self.idMap[x] = i

    def reflectToExcelConfig(self, name):
        if name not in self.idMap:
            return
        column = self.idMap[name]
        sheet = self.activeSheet()
        if sheet is None:
            return
        # pickup
        sheet.Cells(4, column).Value = config.mk_filter(self.filterController.filter[name]["pickup"])
        # ignore
        sheet.Cells(5, column).Value = config.mk_filter(self.filterController.filter[name]["ignore"])
        self.reset()

    def resetAllModel(self):
        self.targetsModel.reset()
        self.conditionsModel.reset()

    def reloadSelection(self):
        if self.targetsLastSelect is None:
            return
        index = self.targetsLastSelect
        target = self.targetsModel.index(index.row(), index.column())
        if target.data() == self.targetsLastSelectText:
            self.targetsSelection.select(target, QItemSelectionModel.ClearAndSelect)

    def setCurrentTarget(self, index):
        """
        :type index: QModelIndex
        :param index: current target index
        """
        self.targetsLastSelect = index
        self.targetsLastSelectText = self.config.columnOrder[index.row()]
        self.setupConditions(self.targetsLastSelectText)

    def currentTargetName(self):
        """
        :rtype: str
        :return: current target key name
        """
        return self.targetsLastSelectText

    def filterConfig(self, name):
        """
        :type name: str
        :param name: config key name
        :rtype: dict[str, list]
        :return: filter config or None
        """
        if name not in self.filterController.filter:
            return None
        return self.filterController.filter[name]

    def setupConditions(self, name):
        # change ui enabled
        #           Add: True
        #  Edit, Remove: False
        self.ui.pushButtonAdd.setEnabled(True)
        self.setEditControlsEnabled(False)
        # check current filter
        conf = self.filterConfig(name)
        if conf is None:
            self.conditionsModel.reset()
            return
        # show filters
        conditions = []
        conditions += [PickupFilter(*x) for x in conf['pickup']]
        conditions += [IgnoreFilter(*x) for x in conf['ignore']]
        self.conditionsModel.setArray(conditions)

    def addCondition(self, key, values, ignore):
        name = self.currentTargetName()
        conf = self.filterConfig(name)
        # check duplicate
        if conf is not None:
            mode = "ignore" if ignore else "pickup"
            for x,y in conf[mode]:
                if x == key and y == values:
                    # already exists
                    self.showMessage(self.tr("condition is already exists"))
                    return
        if not ignore:
            # add pickup
            self.filterController.addPickup(name, key, values)
        else:
            # add ignore
            self.filterController.addIgnore(name, key, values)
        # reflect to Excel
        self.reflectToExcelConfig(name)

    def editCondition(self, index, key, values, ignore):
        name = self.currentTargetName()
        conf = self.filterConfig(name)
        if conf is None:
            return
        row = index.row()
        pickup = True
        if row >= len(conf["pickup"]):
            pickup = False
            row -= len(conf["pickup"])
        if not pickup and row >= len(conf["ignore"]):
            # error
            return
        # check duplicate
        if conf is not None:
            mode = "ignore" if ignore else "pickup"
            for x,y in conf[mode]:
                if x == key and y == values:
                    # already exists
                    self.removeCondition(index)
                    return
        if pickup:
            # edit pickup
            if not ignore:
                self.filterController.editPickup(name, row, key, values)
            else:
                self.removeCondition(index)
                self.addCondition(key, values, ignore)
        else:
            # edit ignore
            if ignore:
                self.filterController.editIgnore(name, row, key, values)
            else:
                self.removeCondition(index)
                self.addCondition(key, values, ignore)
        # reflect to Excel
        self.reflectToExcelConfig(name)

    def removeCondition(self, index):
        name = self.currentTargetName()
        conf = self.filterConfig(name)
        if conf is None:
            return
        row = index.row()
        pickup = True
        if row >= len(conf["pickup"]):
            pickup = False
            row -= len(conf["pickup"])
        if not pickup and row >= len(conf["ignore"]):
            # error
            return
        if pickup:
            # remove pickup
            self.filterController.removePickup(name, row)
        else:
            # remove ignore
            self.filterController.removeIgnore(name, row)
        # reflect to Excel
        self.reflectToExcelConfig(name)

    def setConfig(self, conf):
        self.config = conf
        self.targetsModel.setArray(self.config.columnOrder)
        self.conditionsModel.reset()
        self.filterController = config.FilterController(conf)
        self.reloadSelection()

    def setControlsEnabled(self, enabled):
        for control in self.controls:
            control.setEnabled(enabled)

    def setConditionControlsEnabled(self, enabled):
        """
        set enabled to Add, Edit, Remove

        :type enabled: bool
        :param enabled: state of enabled
        """
        self.ui.pushButtonAdd.setEnabled(enabled)
        self.setEditControlsEnabled(enabled)

    def setEditControlsEnabled(self, enabled):
        """
        set enabled to Edit, Remove

        :type enabled: bool
        :param enabled: state of enabled
        """
        for control in self.editControls:
            control.setEnabled(enabled)

    def setMode(self, mode):
        if mode == Mode.Default:
            self.setControlsEnabled(True)
            self.clearMessage()
        elif mode in [Mode.NotOpen, Mode.Incorrect, Mode.Editing]:
            self.resetAllModel()
            self.setControlsEnabled(False)
            self.ui.pushButtonAdd.setEnabled(False)
            if mode == Mode.NotOpen:
                self.showMessage(self.tr("Excel is not open."))
            elif mode == Mode.Incorrect:
                self.showMessage(self.tr("Active sheet is incorrect format. Please select the correct sheet."))
            elif mode == Mode.Editing:
                self.showMessage(self.tr("Excel is currently in edit mode. You will need to complete the operation."))

    @pyqtSlot()
    def clearMessage(self):
        self.ui.statusbar.clearMessage()

    @pyqtSlot(str, int)
    def showMessage(self, msg, timeout=0):
        self.ui.statusbar.showMessage(msg, timeout)

    @pyqtSlot()
    def on_actionReload_triggered(self):
        pass

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_targetsSelectionChanged(self, selected, deselected):
        if len(selected) != 1:
            return
        index = selected.indexes()[0]
        if not self.targetsSelection.isSelected(index):
            return
        self.setCurrentTarget(index)

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_conditionsSelectionChanged(self, selected, deselected):
        if len(selected) != 1:
            return
        index = selected.indexes()[0]
        if not self.conditionsSelection.isSelected(index):
            return
        self.setEditControlsEnabled(index.isValid())

    @pyqtSlot()
    def on_pushButtonAdd_clicked(self):
        dialog = ConditionDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.addCondition(dialog.key(), dialog.values(), dialog.isIgnore())

    @pyqtSlot()
    def on_pushButtonEdit_clicked(self):
        selected = self.conditionsSelection.selectedIndexes()
        if len(selected) != 1:
            return
        index = selected[0]
        dialog = ConditionDialog(self.config, self)
        dialog.setupByCondition(self.conditionsModel.data(index, models.Role.ObjectRole))
        if dialog.exec_() == QDialog.Accepted and dialog.isChanged():
            self.editCondition(index, dialog.key(), dialog.values(), dialog.isIgnore())

    @pyqtSlot()
    def on_pushButtonRemove_clicked(self):
        selected = self.conditionsSelection.selectedIndexes()
        if len(selected) != 1:
            return
        index = selected[0]
        self.removeCondition(index)


class FilterType:
    PICKUP = 1
    IGNORE = 2

class FilterWrapper(object):

    TYPE = None

    def __init__(self, key, values):
        assert(self.TYPE is not None)
        self.key = key
        self.values = values

    def __str__(self):
        return '"{}": [{}]'.format(self.key, ', '.join(map(str, self.values)))

    def isPickup(self):
        return self.TYPE == FilterType.PICKUP

    def isIgnore(self):
        return self.TYPE == FilterType.IGNORE

class PickupFilter(FilterWrapper):
    TYPE = FilterType.PICKUP

class IgnoreFilter(FilterWrapper):
    TYPE = FilterType.IGNORE


class FilterArrayListModel(models.StrArrayListModel):
    def data(self, index, role):
        if role != Qt.BackgroundRole:
            return super(FilterArrayListModel, self).data(index, role)
        obj = index.data(models.Role.ObjectRole).toPyObject()
        if obj.isPickup():
            return QColor(0x98, 0xfb, 0x98)  # palegreen
        elif obj.isIgnore():
            return QColor(0xf4, 0xa4, 0x60)  # sandybrown
        return super(FilterArrayListModel, self).data(index, role)
