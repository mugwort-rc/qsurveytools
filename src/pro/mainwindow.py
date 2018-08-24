# -*- coding: utf-8 -*-

import re

import pandas
import yaml

from PyQt5.Qt import *

from ..aggregation import SimpleAggregationObject, CrossAggregationObject
from ..aggregation import AggregationCallback
from .. import config
from ..config import Config
from ..config import SafeDumper
from ..config import makeConfigByDataFrame
from ..models import DataFrameTableModel

from .configdialog import ConfigDialog
from .sourceinfodialog import SourceInfoDialog
from .crosstabdialog import CrosstabDialog

from .listdialog import ArraySelectDialog
from .tabledialog import DataFrameDialog, SeriesDialog
from .surveydialog import SimpleSurveyDialog, CrossSurveyDialog

from .ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.SOURCE_FILTER = self.tr('Excel (*.xlsx);;CSV (*.csv)')
        self.CONFIG_FILTER = self.tr('Config (*.yml)')

        self.thread = QThread()
        self.simpleSurvey = None
        self.crossSurvey = None

        self.config = Config()

        self.initUi()

    def initUi(self):
        self.simpleProgress = QProgressBar()
        self.simpleProgress.setVisible(False)
        self.ui.statusbar.addWidget(self.simpleProgress)
        self.crossProgress = QProgressBar()
        self.crossProgress.setVisible(False)
        self.ui.statusbar.addWidget(self.crossProgress)

        self.frameModel = CustomDataFrameTableModel(self)
        self.ui.tableView.setModel(self.frameModel)

        self.ui.tableView.horizontalHeader().sectionDoubleClicked.connect(self.horizontalHeader_sectionDoubleClicked)

    def getOpenFileName(self, filter, caption='', dir=''):
        return QFileDialog.getOpenFileName(self, caption, dir, filter)

    def getSaveFileName(self, filter, caption='', dir=''):
        return QFileDialog.getSaveFileName(self, caption, dir, filter)

    def openExcel(self, filepath, header=0, index_col=None, na_values=None):
        info = QFileInfo(filepath)
        filepath = str(filepath)
        frame = None
        kwargs = {
            'header': header,
            'index_col': index_col,
            'na_values': na_values,
        }
        if info.suffix() == 'xlsx':
            frame = pandas.read_excel(filepath, sheetname=0, **kwargs)
        elif info.suffix() == 'csv':
            frame = pandas.read_csv(filepath, **kwargs)
        else:
            self.showMessage(self.tr('Unsupported file extension.'))
            return None
        return frame

    def openFile(self, filepath, header=0, index_col=None, na_values=None):
        frame = self.openExcel(filepath, header=header, index_col=index_col, na_values=na_values)
        if frame is None:
            return
        self.frameModel.setDataFrame(frame)
        self.originalFrame = frame

    def setConfig(self, config):
        self.config = Config(config)
        self.frameModel.setConfig(self.config)

    def showMessage(self, msg, time=0):
        self.ui.statusbar.showMessage(msg, time)

    @pyqtSlot()
    def on_actionNew_triggered(self):
        self.frameModel.setDataFrame(pandas.DataFrame())

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        filepath = self.getOpenFileName(self.SOURCE_FILTER)
        if filepath.isEmpty():
            return
        self.openFile(filepath)

    @pyqtSlot()
    def on_actionOpenWith_triggered(self):
        filepath = self.getOpenFileName(self.SOURCE_FILTER)
        if filepath.isEmpty():
            return
        dialog = SourceInfoDialog(self)
        dialog.setFilePath(filepath)
        if dialog.exec_() == QDialog.Accepted:
            header = dialog.header()
            index_col = dialog.index_col()
            na_values = dialog.na_values()
            filepath = dialog.filePath()
            if filepath.isEmpty():
                return
            self.openFile(filepath, header=header, index_col=index_col, na_values=na_values)

    @pyqtSlot()
    def on_actionSave_triggered(self):
        frame = self.frameModel.dataFrame()
        if frame is None:
            return
        filepath = self.getSaveFileName(self, self.SOURCE_FILTER)
        if filepath.isEmpty():
            return
        info = QFileInfo(filepath)
        if info.suffix() == 'xlsx':
            frame.to_excel(str(filepath))
        elif info.suffix() == 'csv':
            frame.to_csv(str(filepath))

    @pyqtSlot()
    def on_actionAggregate_triggered(self):
        # check frame
        frame = self.frameModel.dataFrame()
        if frame is None:
            return
        dialog = SimpleSurveyDialog()
        self.simpleCallback = AggregationQObject(dialog)
        self.simpleCallback.initialized.connect(self.startSimpleProgress)
        self.simpleCallback.updated.connect(self.simpleProgress.setValue)
        self.simpleCallback.finished.connect(self.simpleFinished)
        self.simpleSurvey = SimpleAggregationObject(self.simpleCallback, self.config, frame)
        self.simpleSurvey.moveToThread(self.thread)
        self.thread.start()
        #self.simpleSurvey.simpleSurvey()
        QMetaObject.invokeMethod(self.simpleSurvey, "simpleSurvey")

    @pyqtSlot()
    def on_actionCrosstab_triggered(self):
        # check frame
        frame = self.frameModel.dataFrame()
        if frame is None:
            return
        dialog = CrossSurveyDialog()
        self.crossSurvey = CrossSurveyObject(dialog, self.config, frame)
        self.crossSurvey.initialize.connect(self.startCrossProgress)
        self.crossSurvey.update.connect(self.crossProgress.setValue)
        self.crossSurvey.finished.connect(self.crossFinished)
        self.crossSurvey.moveToThread(self.thread)
        self.thread.start()
        #self.crossSurvey.crossSurvey()
        QMetaObject.invokeMethod(self.crossSurvey, "crossSurvey")

    @pyqtSlot(bool)
    def on_actionMappedData_toggled(self, checked):
        self.frameModel.setShowChoice(checked)

    @pyqtSlot()
    def on_actionCreateConfig_triggered(self):
        filepath = self.getOpenFileName(self.SOURCE_FILTER)
        if filepath.isEmpty():
            return
        frame = self.openExcel(filepath)
        if frame.columns[0] != 'ID':
            self.showMessage("Invalid form.")
            return
        self.setConfig(makeConfigByDataFrame(frame))

    @pyqtSlot()
    def on_actionEditConfig_triggered(self):
        dialog = ConfigDialog(self)
        dialog.setConfig(self.config)
        if dialog.exec_() == QDialog.Accepted:
            self.setConfig(dialog.getConfig())

    @pyqtSlot()
    def on_actionLoadConfig_triggered(self):
        filepath = self.getOpenFileName(self.CONFIG_FILTER)
        if filepath.isEmpty():
            return
        data = yaml.load(open(str(filepath)).read().decode('utf-8'))
        self.setConfig(data)

    @pyqtSlot()
    def on_actionSaveConfig_triggered(self):
        filepath = self.getSaveFileName(self.CONFIG_FILTER)
        if filepath.isEmpty():
            return
        if not filepath.endsWith('.yml'):
            filepath += '.yml'
        dumped = yaml.dump(self.config, allow_unicode=True, default_flow_style=False, Dumper=SafeDumper)
        open(str(filepath), 'w').write(dumped)

    @pyqtSlot(int)
    def horizontalHeader_sectionDoubleClicked(self, index):
        frame = self.frameModel.dataFrame()
        if frame is None:
            return
        dialog = CustomSeriesDialog(self)
        obj = SimpleSurveyObject(dialog, self.config, frame)
        obj.value_counts(frame.columns[index])
        dialog.open()

    @pyqtSlot(int)
    def startSimpleProgress(self, maximum):
        self.simpleProgress.setValue(0)
        self.simpleProgress.setMaximum(maximum)
        self.simpleProgress.setVisible(True)

    @pyqtSlot(int)
    def startCrossProgress(self, maximum):
        self.crossProgress.setValue(0)
        self.crossProgress.setMaximum(maximum)
        self.crossProgress.setVisible(True)

    @pyqtSlot(QDialog)
    def simpleFinished(self, dialog):
        dialog.open()
        self.simpleProgress.setVisible(False)
        self.thread.exit(0)

    @pyqtSlot(QDialog)
    def crossFinished(self, dialog):
        dialog.open()
        self.crossProgress.setVisible(False)
        self.thread.exit(0)

class CustomDataFrameTableModel(DataFrameTableModel):
    def __init__(self, parent=None):
        super(CustomDataFrameTableModel, self).__init__(parent)
        self.filter = None
        self.config = Config()
        self.choiceMap = {}
        self.typeMap = {}
        self.showChoice = False

    def presentationChanged(self):
        start = self.index(0, 0)
        end = self.index(self.rowCount(), self.columnCount())
        self.dataChanged.emit(start, end)

    def setFilter(self, filter):
        self.filter = filter

    def setConfig(self, config):
        self.config = config
        self.buildMaps()
        self.presentationChanged()

    def buildMaps(self):
        frame = self.dataFrame()
        if frame is None:
            return
        self.choiceMap = {}
        self.typeMap = {}
        for i,column in enumerate(frame.columns):
            self.choiceMap[i] = {}
            conf = self.config.columns.get(column, {})
            self.typeMap[i] = conf.get('type', 0)
            if not conf:
                continue
            for j,item in enumerate(conf.get('choice', []), 1):
                self.choiceMap[i][j] = item
        self.setFilter(config.FilterController(self.config))

    def setShowChoice(self, showChoice):
        self.showChoice = showChoice
        self.presentationChanged()

    def setDataFrame(self, frame):
        super(CustomDataFrameTableModel, self).setDataFrame(frame)
        self.columnsMap = {x:i for i,x in enumerate(self.frame.columns)}
        self.buildMaps()

    def data(self, index, role=Qt.DisplayRole):
        ret = super(CustomDataFrameTableModel, self).data(index, role)
        if role == Qt.DisplayRole and self.showChoice:
            return self.mappedData(index, ret)
        if role == Qt.BackgroundRole and self.filter is not None:
            if self.filter.isIgnore(self.dataFrame(), index.row(), index.column()):
                return QColor(Qt.gray)
        return ret

    def mappedData(self, index, data):
        if not self.typeMap:
            return data
        column = index.column()
        type = self.typeMap[column]
        if type == 0:
            return data
        if isinstance(data, QVariant):
            data = data.toPyObject()
        if data is None:
            return data
        if type == 1:
            try:
                value = int(data)
                return self.choiceMap[column][value]
            except Exception, e:
                print 'Error at ({},{}): "{}"'.format(index.row(), index.column(), e)
        elif type == 2:
            try:
                values = map(int, re.split(ur'\s*,\s*', str(data)))
                texts = [self.choiceMap[column][x] for x in values]
                return u','.join(texts)
            except Exception, e:
                print 'Error at ({},{}): "{}"'.format(index.row(), index.column(), e)
        return data


class CustomSeriesDialog(SeriesDialog):
    def addSeries(self, name, series):
        self.setWindowTitle(name)
        self.setSeries(series)


class AggregationQObject(QObject, AggregationCallback):

    initialized = pyqtSignal(int)
    updated = pyqtSignal(int)
    finished = pyqtSignal(QDialog)

    def __init__(self, dialog, parent=None):
        super(AggregationQObject, self).__init__(parent)
        self.dialog = dialog

    def initialize(self, maximum):
        self.initialized.emit(maximum)

    def update(self, current):
        self.updated.emit(current)

    def finish(self):
        self.finished.emit(self.dialog)

    def addSeries(self, series):
        self.dialog.addSeries(series)

    def addDataFrame(self, frame):
        self.dialog.addDataFrame(frame)
