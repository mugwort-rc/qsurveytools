# -*- coding: utf-8 -*-

import pandas
import six
from xlsxwriter.utility import xl_col_to_name

import win32com.client
from pywintypes import com_error
from ..win32 import constants
from ..win32 import excel

from PyQt4.Qt import *

from .. import config
from .. import cursor
from .. import events
from ..models import ArrayListModel
from .. import qsource
from .. import qvalidator

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

        self.setWindowTitle(self.tr('checktool'))

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.ui.statusbar.addWidget(self.progressBar)
        self.progressBar.setValue(0)

        self.model = ArrayListModel(self)
        self.ui.listView.setModel(self.model)

        self.XL = None

    def activeBook(self):
        with cursor.BusyCursor(self):
            if self.XL is None:
                self.XL = win32com.client.Dispatch('Excel.Application')
            try:
                result = self.XL.ActiveWorkbook
                return result
            except (AttributeError, com_error) as e:
                return None

    @pyqtSlot(QString)
    def addMessage(self, text):
        self.model.setArray(self.model.array()+[text])

    def clearMessage(self):
        self.model.setArray([])

    def setProgressObject(self, obj):
        """
        :type obj: qaggregation.QAggregationObject
        """
        obj.initialized.connect(self.progressInit)
        obj.updated.connect(self.progressBar.setValue)

    @pyqtSlot(int)
    def progressInit(self, maximum):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(maximum)

    @pyqtSlot()
    def on_pushButtonStart_clicked(self):
        book = self.activeBook()
        if book is None:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please open the Excel book."))
            return

        sheet_setting = qsource.Source.sheet_setting()
        sheet_cross = qsource.Source.sheet_cross()
        sheet_source = qsource.Source.sheet_source()

        names = [
            sheet_setting,
            sheet_cross,
            sheet_source,
        ]

        sheets = excel.collect_sheets(book, names)

        no_error = True
        for name in names:
            if name not in sheets:
                self.sheetNotFound(name)
                no_error = False
        if not no_error:
            return

        try:
            settingFrame = excel.byUsedRange(sheets[sheet_setting].UsedRange())
        except:
            settingFrame = None
            self.sheetCannotLoad(sheet_setting)
        try:
            crossFrame = excel.byUsedRange(sheets[sheet_cross].UsedRange(), index_col=0)
        except:
            crossFrame = None
            self.sheetCannotLoad(sheet_cross)
        try:
            sourceFrame = excel.byUsedRange(sheets[sheet_source].UsedRange())
        except:
            sourceFrame = None
            self.sheetCannotLoad(sheet_source)

        if settingFrame is None or crossFrame is None or sourceFrame is None:
            return

        def invalidSource(name):
            self.addMessage(self.tr('Error: Sheet "%1" is invalid format.').arg(name))

        no_error = True
        if not qsource.Source.isSettingFrame(settingFrame):
            invalidSource(sheet_setting)
            no_error = False
        if not qsource.Source.isCrossFrame(crossFrame):
            invalidSource(sheet_cross)
            no_error = False
        if not qsource.Source.isSourceFrame(sourceFrame):
            invalidSource(sheet_source)
            no_error = False
        if not no_error:
            return

        self.clearSourceMarker(sheets[sheet_source])

        # drop TITLE helper
        sourceFrame = sourceFrame.ix[1:]
        # drop ID NaN
        sourceFrame = sourceFrame[sourceFrame[qsource.Source.setting_id()].notnull()]

        conf = config.makeConfigByDataFrame(settingFrame, crossFrame)

        self.validator = CustomValidationObject(sheets[sheet_source], self)
        self.setProgressObject(self.validator)
        self.progressBar.setVisible(True)
        self.validator.finished.connect(self.validationFinished)
        self.validator.validate(conf, sourceFrame)  # no threading

    def sheetNotFound(self, name):
        self.addMessage(self.tr('Error: Sheet "%1" is not found.').arg(name))

    def sheetCannotLoad(self, name):
        self.addMessage(self.tr('Error: Sheet "%1" load failed.').arg(name))

    def clearSourceMarker(self, sheet):
        used = sheet.UsedRange()
        height = len(used)
        if height <= 0:
            return
        width = len(used[0])
        rng = sheet.Range("A3:{}{}".format(xl_col_to_name(width-1), height))
        rng.Interior.Pattern = constants.constants.xlNone

    @pyqtSlot(bool)
    def validationFinished(self, error):
        self.progressBar.setVisible(False)
        self.validation_error = error
        if error:
            self.model.setArray(self.model.array()+self.validator.messages)


class CustomValidationObject(qvalidator.QValidationObject):
    def __init__(self, sheet, parent=None):
        """
        :type sheet: win32com.client.Object
        :type parent: QObject
        """
        self.sheet = sheet
        self.last_sheet = None
        super(CustomValidationObject, self).__init__(parent)

        self._column_map = {x:i for i,x in enumerate(self.sheet.UsedRange()[0])}

    def setError(self, column, row):
        if column not in self._column_map:
            return
        column = self._column_map[column]
        self.sheet.Range("A{}".format(row+2)).Interior.Color = win32com.client.constants.rgbYellow
        self.last_sheet = "{}{}".format(xl_col_to_name(column), row+2)
        self.sheet.Range(self.last_sheet).Interior.Color = win32com.client.constants.rgbYellow

    def validationError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).validationError(column, row, value, **kwargs)

    def multipleExceptionError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).multipleExceptionError(column, row, value, **kwargs)

    def limitationError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).limitationError(column, row, value, **kwargs)