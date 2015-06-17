# -*- coding: utf-8 -*-

import pandas
import six
import xlrd
import yaml

from PyQt4.Qt import *

from .. import qaggregation
from .. import config
from ..cursor import BusyCursor
from .. import events
from ..models import ArrayListModel
from ..utils import expand_multiple
from .. import qvalidator
from .. import source
from .. import status

from ui_mainwindow import Ui_MainWindow

TEMPLATE_SETTING_PATH = "./.config/template.conf"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.SOURCE_FILTER = self.tr('Excel (*.xlsx *.xlsm);;CSV (*.csv)')
        self.OUTPUT_FILTER = self.tr('Excel (*.xlsx)')
        self.lastDirectory = ''

        self.setWindowTitle(self.tr('surveytool'))
        self.ui.progressBar.setValue(0)
        self.ui.progressBarGeneral.setValue(0)
        self.ui.progressBarGeneral.setMaximum(2)

        self.file_dd_filter = events.FileDragAndDropFilter()
        self.line_edits = [
            self.ui.lineEditInput,
            self.ui.lineEditOutput,
        ]
        for lineEdit in self.line_edits:
            lineEdit.installEventFilter(self.file_dd_filter)
            lineEdit.textChanged.connect(self.setWorkable)

        self.setWorkable()

        self.model = ArrayListModel(self)
        self.ui.listView.setModel(self.model)

        self.simple_aggregation = None
        self.cross_aggregation = None
        self.simple_thread = QThread()
        self.cross_thread = QThread()

        self.validator = None
        self.validation_error = False

    def getOpenFileName(self, filter, caption='', dir=None):
        if dir is None:
            dir = self.lastDirectory
        result = QFileDialog.getOpenFileName(self, caption, dir, filter)
        self.setLastDirectory(result)
        return result

    def getSaveFileName(self, filter, caption='', dir=None):
        if dir is None:
            dir = self.lastDirectory
        result = QFileDialog.getSaveFileName(self, caption, dir, filter)
        self.setLastDirectory(result)
        return result

    def getExistingDirectory(self, caption='', dir=None):
        if dir is None:
            dir = self.lastDirectory
        result = QFileDialog.getExistingDirectory(self, caption, dir)
        self.setLastDirectory(result)
        return result

    def setLastDirectory(self, filepath):
        if not filepath:
            return
        self.lastDirectory = QFileInfo(filepath).dir().path()

    def openExcel(self, filepath, header=0, index_col=None, na_values=None):
        info = QFileInfo(filepath)
        filepath = str(filepath)
        frame = None
        kwargs = {
            'header': header,
            'index_col': index_col,
            'na_values': na_values,
        }
        if info.suffix() in ['xlsx', 'xlsm']:
            frame = pandas.read_excel(filepath, sheetname=0, **kwargs)
        elif info.suffix() == 'csv':
            frame = pandas.read_csv(filepath, **kwargs)
        else:
            return None
        return frame

    def setProgressObject(self, obj):
        """
        :type obj: qaggregation.QAggregationObject
        """
        obj.initialized.connect(self.progressInit)
        obj.updated.connect(self.ui.progressBar.setValue)

    def invoke_aggregate(self, obj, conf, frame, dropna):
        strings = {
            'TOTAL': six.text_type(self.tr('TOTAL')),
            'BLANK': six.text_type(self.tr('BLANK')),
        }
        QMetaObject.invokeMethod(obj, "aggregate",
                                 Q_ARG(config.Config, conf),
                                 Q_ARG(pandas.DataFrame, frame),
                                 Q_ARG(bool, dropna),
                                 Q_ARG(dict, strings))

    @pyqtSlot(QString)
    def addMessage(self, text):
        self.model.setArray(self.model.array()+[text])

    def clearMessage(self):
        self.model.setArray([])

    def showMessageTab(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.tabMessage)

    @pyqtSlot()
    def on_toolButtonInput_clicked(self):
        filepath = self.getOpenFileName(self.SOURCE_FILTER)
        if not filepath:
            return
        self.ui.lineEditInput.setText(filepath)

    @pyqtSlot()
    def on_toolButtonSource_clicked(self):
        filepath = self.getOpenFileName(self.SOURCE_FILTER)
        if not filepath:
            return
        self.ui.lineEditSource.setText(filepath)

    @pyqtSlot()
    def on_toolButtonOutput_clicked(self):
        filepath = self.getExistingDirectory()
        if not filepath:
            return
        self.ui.lineEditOutput.setText(filepath)

    @pyqtSlot()
    def setWorkable(self):
        input_info = QFileInfo(self.ui.lineEditInput.text())
        output_info = QFileInfo(self.ui.lineEditOutput.text())
        workable = (
            input_info.exists() and input_info.isFile() and
            output_info.exists() and output_info.isDir() and
            not self.simple_thread.isRunning() and
            not self.cross_thread.isRunning()
        )
        self.ui.pushButtonSimple.setEnabled(workable)
        self.ui.pushButtonCross.setEnabled(workable)

    @pyqtSlot()
    def on_pushButtonSimple_clicked(self):
        self.ui.pushButtonSimple.setEnabled(False)
        self.ui.pushButtonCross.setEnabled(False)
        dropna = self.ui.checkBoxDropNA.isChecked()
        conf, frame, filepath = self.loadSources()
        if filepath is None or not QFileInfo(filepath).isDir():
            if filepath is None:
                self.addMessage(self.tr('Error: config load failed.'))
            elif not QFileInfo(filepath).isDir():
                self.addMessage(self.tr('Error: output file path is not directory.'))
            self.showMessageTab()
            return

        self.simple_aggregation = SimpleAggregationObject(conf, QDir(filepath).filePath(self.tr('simple.xlsx')))
        self.setProgressObject(self.simple_aggregation)
        self.simple_aggregation.finished.connect(self.simpleFinished)

        self.simple_aggregation.moveToThread(self.simple_thread)
        self.simple_thread.start()
        #self.simple_aggregation.aggregate()
        self.invoke_aggregate(self.simple_aggregation, conf, frame, dropna)

    @pyqtSlot()
    def on_pushButtonCross_clicked(self):
        self.ui.pushButtonSimple.setEnabled(False)
        self.ui.pushButtonCross.setEnabled(False)
        dropna = self.ui.checkBoxDropNA.isChecked()
        conf, frame, filepath = self.loadSources()
        if filepath is None or not QFileInfo(filepath).isDir():
            if filepath is None:
                self.addMessage(self.tr('Error: config load failed.'))
            elif not QFileInfo(filepath).isDir():
                self.addMessage(self.tr('Error: output file path is not directory.'))
            self.showMessageTab()
            return

        self.cross_aggregation = CrossAggregationObject(conf, QDir(filepath).filePath(self.tr('cross.xlsx')))
        self.setProgressObject(self.cross_aggregation)
        self.cross_aggregation.finished.connect(self.crossFinished)
        self.cross_aggregation.moveToThread(self.cross_thread)
        self.cross_thread.start()
        #self.cross_aggregation.aggregate()
        self.invoke_aggregate(self.cross_aggregation, conf, frame, dropna)

    def loadSources(self):
        self.ui.progressBarGeneral.setValue(0)
        self.ui.progressBar.setValue(0)
        self.clearMessage()
        # load source
        with status.MainWindowStatus(self) as state:
            state.setMessage(self.tr("loading..."))
            inputFilePath = six.text_type(self.ui.lineEditInput.text())
            if not QFile.exists(inputFilePath):
                self.addMessage(self.tr('Error: Input "%1" not found.').arg(inputFilePath))
                self.showMessageTab()
                return None, None, None
            self.addMessage(self.tr('Input: "%1"').arg(inputFilePath))
            tmpl_conf = source.TemplateSetting.from_yaml(TEMPLATE_SETTING_PATH)
            try:
                frames = self.load_excel_sheets(inputFilePath, [0, 1, 2] + tmpl_conf.sheet_names())
                if not frames:
                    raise Exception
            except:
                raise
                self.addMessage(self.tr('Error: Input "%1" load failed.').arg(inputFilePath))
                self.showMessageTab()
                return None, None, None

            def detect_key(data, keys):
                for key in keys:
                    if key in data:
                        return key
                return None

            setting_key = detect_key(frames, [tmpl_conf.sheet_setting, 0])
            cross_key = detect_key(frames, [tmpl_conf.sheet_cross, 1])
            has_cross = cross_key is not None and 2 in frames
            source_key = detect_key(frames, [tmpl_conf.sheet_source, (2 if has_cross else 1)])

            settingFrame = frames[setting_key]
            crossFrame = None
            if has_cross:
                crossFrame = frames[cross_key]
            sourceFrame = frames[source_key]
            # drop TITLE helper
            sourceFrame = sourceFrame.ix[1:]
            # drop ID NaN
            sourceFrame = sourceFrame[sourceFrame['ID'].notnull()]

            conf = config.makeConfigByDataFrame(settingFrame, crossFrame)

        self.ui.progressBarGeneral.setValue(1)

        # validation
        with status.MainWindowStatus(self) as state:
            state.setMessage(self.tr("validating..."))
            self.validator = qvalidator.QValidationObject(self)
            self.setProgressObject(self.validator)
            self.validator.finished.connect(self.validationFinished)
            self.validator.validate(conf, sourceFrame)  # no threading

        self.ui.progressBarGeneral.setValue(2)

        outputFilePath = six.text_type(self.ui.lineEditOutput.text())

        return conf, sourceFrame, outputFilePath

    def load_excel_sheets(self, path, sheets):
        book = xlrd.open_workbook(path)
        names = book.sheet_names()
        size = len(book.sheets())
        temp = []
        for sheet in sheets:
            if ((isinstance(sheet, six.string_types) and sheet in names) or
                (isinstance(sheet, int) and sheet < size)):
                temp.append(sheet)
        result = {}
        for index in temp:
            result[index] = pandas.read_excel(path, sheetname=index)
        return result

    @pyqtSlot(int)
    def progressInit(self, maximum):
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(maximum)

    @pyqtSlot()
    def simpleFinished(self):
        self.simple_thread.exit(0)
        with BusyCursor(self):
            ret = self.simple_aggregation.save()
        self.ui.pushButtonSimple.setEnabled(True)
        self.ui.pushButtonCross.setEnabled(True)
        if ret:
            QMessageBox.information(self, self.tr('Finished'), self.tr('Finished.'))
        else:
            QMessageBox.information(self, self.tr('Error'), self.tr('Write error.'))
        if self.validation_error:
            self.showMessageTab()

    @pyqtSlot()
    def crossFinished(self):
        self.cross_thread.exit(0)
        with BusyCursor(self):
            ret = self.cross_aggregation.save()
        self.ui.pushButtonSimple.setEnabled(True)
        self.ui.pushButtonCross.setEnabled(True)
        if ret:
            QMessageBox.information(self, self.tr('Finished'), self.tr('Finished.'))
        else:
            QMessageBox.information(self, self.tr('Error'), self.tr('Write error.'))
        if self.validation_error:
            self.showMessageTab()

    @pyqtSlot(bool)
    def validationFinished(self, error):
        self.validation_error = error
        if error:
            self.model.setArray(self.model.array()+self.validator.messages)


class SimpleAggregationObject(qaggregation.SimpleAggregationObject):
    def __init__(self, conf, filepath, parent=None):
        super(SimpleAggregationObject, self).__init__(parent)
        self.config = conf
        self.filepath = filepath
        self.series = {}

    def addSeries(self, name, series):
        self.series[name] = series

    def save(self):
        from .. import excel
        book = excel.SurveyExcelBook(unicode(self.filepath))
        sheet = book.worksheet(unicode(self.tr('SimpleAggregation')))
        for column in self.config.columnOrder:
            if column not in self.series:
                continue
            sheet.setTitle(self.config.columns.get(column, {}).get('title', ''))
            sheet.paste(self.series[column])
            sheet.addPadding(3)
        try:
            book.close()
        except IOError:
            return False
        return True


class CrossAggregationObject(qaggregation.CrossAggregationObject):
    def __init__(self, conf, filepath, parent=None):
        super(CrossAggregationObject, self).__init__(parent)
        self.config = conf
        self.filepath = filepath
        self.frames = {}

    def addDataFrame(self, key, target, frame):
        if target not in self.frames:
            self.frames[target] = {}
        self.frames[target][key] = frame

    def save(self):
        from .. import excel
        book = excel.SurveyExcelBook(unicode(self.filepath))
        for target in self.config.cross.targets:
            if target.id not in self.frames:
                continue
            sheet = book.worksheet((target.name if target.name else target.id)[:31])
            sheet.setTitle(self.config.columns.get(target.id, {}).get('title', ''))
            sheet.addPadding(2)
            for key in self.config.cross.keys:
                if key.id not in self.frames[target.id]:
                    continue
                sheet.setTitle(self.config.columns.get(key.id, {}).get('title', ''))
                sheet.paste(self.frames[target.id][key.id])
                sheet.addPadding(2)
        try:
            book.close()
        except IOError:
            return False
        return True
