# -*- coding: utf-8 -*-

import pandas
import six

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

        def sheetNotFound(name):
            self.addMessage(self.tr('Error: Sheet "%1" is not found.').arg(name))

        no_error = True
        for name in names:
            if name not in sheets:
                sheetNotFound(name)
                no_error = False
        if not no_error:
            return

        def sheetCannotLoad(name):
            self.addMessage(self.tr('Error: Sheet "%1" load failed.').arg(name))

        try:
            settingFrame = excel.byUsedRange(sheets[sheet_setting].UsedRange())
        except:
            settingFrame = None
            sheetCannotLoad(sheet_setting)
        try:
            crossFrame = excel.byUsedRange(sheets[sheet_cross].UsedRange(), index_col=0)
        except:
            crossFrame = None
            sheetCannotLoad(sheet_cross)
        try:
            sourceFrame = excel.byUsedRange(sheets[sheet_source].UsedRange())
        except:
            sourceFrame = None
            sheetCannotLoad(sheet_source)

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

        # drop TITLE helper
        sourceFrame = sourceFrame.ix[1:]
        # drop ID NaN
        sourceFrame = sourceFrame[sourceFrame[qsource.Source.setting_id()].notnull()]

        conf = config.makeConfigByDataFrame(settingFrame, crossFrame)

        self.validator = qvalidator.QValidationObject(self)
        self.setProgressObject(self.validator)
        self.validator.finished.connect(self.validationFinished)
        self.validator.validate(conf, sourceFrame)  # no threading

    @pyqtSlot(bool)
    def validationFinished(self, error):
        self.validation_error = error
        if error:
            self.model.setArray(self.model.array()+self.validator.messages)
