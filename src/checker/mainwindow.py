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
from .. import models
from .. import qerror
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

        self.load_error_count = 0
        self.config_callback = None
        self.config_error_count = 0
        self.validator = None

        self.error_ctx = qerror.SurveyErrorContext(self)
        self.ui.listView.setModel(self.error_ctx.model())

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

        # clear last states.
        self.error_ctx.clear()
        self.ui.statusbar.clearMessage()

        # start loading
        self.error_ctx.setLoading()

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
            self.error_ctx.addMessage(self.tr('Error: Sheet "%1" is invalid format.').arg(name))

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

        # start parsing
        self.error_ctx.setParsing()
        self.config_callback = ConfigValidationObject(
            sheets[sheet_setting],
            sheets[sheet_cross],
            sheets[sheet_source],
            self
        )
        self.config_callback.warning.connect(self.error_ctx.addMessage)
        conf = config.makeConfigByDataFrame(settingFrame, crossFrame, self.config_callback)

        # start validating
        self.error_ctx.setValidating()
        validation_args = {
            "noticeForbidden": self.ui.checkBoxCheckForbiddenErrors.isChecked(),
        }
        self.validator = CustomValidationObject(conf, sheets[sheet_source], self, **validation_args)
        self.setProgressObject(self.validator)
        self.progressBar.setVisible(True)
        self.validator.finished.connect(self.validationFinished)
        self.validator.validate(sourceFrame)  # no threading
        self.validator.selectError(-1)  # select last error

    def sheetNotFound(self, name):
        self.error_ctx.addMessage(self.tr('Error: Sheet "%1" is not found.').arg(name))

    def sheetCannotLoad(self, name):
        self.error_ctx.addMessage(self.tr('Error: Sheet "%1" load failed.').arg(name))

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
            self.error_ctx.addMessages(self.validator.messages)
        self.ui.statusbar.showMessage(self.tr("finished."), 0)

    @pyqtSlot(QModelIndex)
    def on_listView_doubleClicked(self, index):
        if self.validator is None:
            return
        ctx = self.error_ctx.errorContext(index.row())
        if ctx < 0:
            return
        if ctx == qerror.SurveyErrorContext.LOAD:
            return
        elif ctx == qerror.SurveyErrorContext.PARSE:
            row = self.error_ctx.errorIndex(index.row())
            self.config_callback.selectError(row)
        elif ctx == qerror.SurveyErrorContext.VALIDATE:
            row = self.error_ctx.errorIndex(index.row())
            self.validator.selectError(row)


class ConfigValidationObject(QObject, config.ConfigCallback):

    warning = pyqtSignal(QString)

    DUPLICATED = 1
    RESERVED = 2

    def __init__(self, setting, cross, source, parent):
        """
        :type setting: win32com.client.Object
        :type cross: win32com.client.Object
        :type source: win32com.client.Object
        :type parent: QObject

        :param parent: parent object
        """
        super(ConfigValidationObject, self).__init__(parent)
        self.setting_sheet = setting
        self.cross_sheet = cross
        self.source_sheet = source
        self.errors = []

    def duplicatedChoice(self, column):
        """
        :type column: str
        :param column: name of error column
        """
        self.errors.append((self.DUPLICATED, column))
        self.warning.emit(self.tr('column "%1" has duplicate choices.').arg(column))

    def reservedChoice(self, column):
        """
        :type column: str
        :param column: name of error column
        """
        self.errors.append((self.RESERVED, column))
        self.messages_.append(self.tr('column "%1" has reserved name.').arg(column))

    def selectError(self, index):
        # check range
        if index < 0 or len(self.errors) <= index:
            return
        reason, value = self.errors[index]
        if reason in [self.DUPLICATED, self.RESERVED]:
            used = self.setting_sheet.UsedRange()
            for i, v in enumerate(used[0]):
                if v != value:
                    continue
                self.setting_sheet.Activate()
                self.setting_sheet.Range("{0}:{0}".format(xl_col_to_name(i))).Select()
                break


class CustomValidationObject(qvalidator.QValidationObject):
    def __init__(self, conf, sheet, parent=None, **kwargs):
        """
        :type sheet: win32com.client.Object
        :type parent: QObject
        """
        self.sheet = sheet
        self.last_error = None
        super(CustomValidationObject, self).__init__(conf, parent, **kwargs)

        self._column_map = {x:i for i,x in enumerate(self.sheet.UsedRange()[0])}
        self._error_map = {}

    def selectError(self, index):
        # selectError(-1) select last error.
        if index < 0 and self.last_error is not None:
            column, row = self.last_error
        # detect by error number.
        else:
            if index not in self._error_map:
                return
            column, row = self._error_map[index]
        try:
            self.sheet.Activate()
            self.sheet.Range("{}{}".format(xl_col_to_name(column), row)).Select()
        except:
            pass

    def setError(self, column, row):
        if column not in self._column_map:
            return
        column = self._column_map[column]
        row += 2
        self.last_error = (column, row)
        self._error_map[len(self._error_map)] = (column, row)
        try:
            self.sheet.Range("A{}".format(row)).Interior.Color = win32com.client.constants.rgbYellow
            self.sheet.Range("{}{}".format(xl_col_to_name(column), row)).Interior.Color = win32com.client.constants.rgbYellow
        except:
            pass

    def validationError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).validationError(column, row, value, **kwargs)

    def multipleExceptionError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).multipleExceptionError(column, row, value, **kwargs)

    def limitationError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).limitationError(column, row, value, **kwargs)

    def forbiddenError(self, column, row, value, **kwargs):
        if self.noticeForbidden:
            self.setError(column, row)
        super(CustomValidationObject, self).forbiddenError(column, row, value, **kwargs)

    def incompleteError(self, column, row, value, **kwargs):
        self.setError(column, row)
        super(CustomValidationObject, self).incompleteError(column, row, value, **kwargs)
