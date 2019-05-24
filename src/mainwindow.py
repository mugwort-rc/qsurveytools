# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import enum
import os

import pandas
import xlrd
import yaml

from PyQt5.Qt import *

from . import analyzer
from . import qaggregation
from . import config
from .cursor import BusyCursor
from . import events
from .models import ArrayListModel
from . import utils
from . import qsource
from . import qvalidator
from . import status

from .ui_mainwindow import Ui_MainWindow


class CrossFormat(enum.Enum):
    Default = 0
    SingleTable = 1
    Azemichi = 2
    AzemichiAdvanced = 3


class ExceptionBase(Exception):
    pass

class LoadException(ExceptionBase):
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.SOURCE_FILTER = self.tr('Excel (*.xlsx *.xlsm);;CSV (*.csv)')
        self.OUTPUT_FILTER = self.tr('Excel (*.xlsx)')
        self.lastDirectory = ''
        self.STRINGS = {
            "TOTAL": str(self.tr("TOTAL")),
            "BLANK": str(self.tr("BLANK")),
            "ERROR": str(self.tr("ERROR")),
        }

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
            lineEdit.textChanged.connect(self.updateWorkable)

        self.updateWorkable()

        self.model = ArrayListModel(self)
        self.ui.listView.setModel(self.model)

        # output format of cross
        self.crossModel = QStringListModel(self)
        self.crossModel.setStringList([
            self.tr("Default"),
            self.tr("SingleTable"),
            self.tr("Azemichi"),
            self.tr("Azemichi (advanced)"),
        ])
        self.crossEnums = [
            CrossFormat.Default,
            CrossFormat.SingleTable,
            CrossFormat.Azemichi,
            CrossFormat.AzemichiAdvanced,
        ]
        self.ui.comboBoxCrossFormat.setModel(self.crossModel)

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

    def invoke_aggregate(self, obj, conf, frame, dropna, options):
        QMetaObject.invokeMethod(obj, "aggregate",
                                 Q_ARG(config.Config, conf),
                                 Q_ARG(pandas.DataFrame, frame),
                                 Q_ARG(bool, dropna),
                                 Q_ARG(dict, self.STRINGS),
                                 Q_ARG(dict, options))

    @pyqtSlot(str)
    def addMessage(self, text):
        self.model.setArray(self.model.array()+[text])

    @pyqtSlot(list)
    def addMessages(self, texts):
        self.model.setArray(self.model.array()+texts)

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
    def updateWorkable(self):
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
        self.ui.pushButtonExpand.setEnabled(workable)

    @pyqtSlot()
    def on_pushButtonSimple_clicked(self):
        self.ui.pushButtonSimple.setEnabled(False)
        self.ui.pushButtonCross.setEnabled(False)
        dropna = self.ui.checkBoxDropNA.isChecked()
        aggregate_options = self.get_aggregate_options()
        try:
            conf, frame, filepath = self.loadSources(**aggregate_options)
        except LoadException:
            self.addMessage(self.tr('Error: config load failed.'))
            self.showMessageTab()
            return

        with_percent = self.ui.checkBoxWithPercent.isChecked()
        sa_to_pie = self.ui.checkBoxSAToPie.isChecked()
        gen_abstract = self.ui.checkBoxAnalyzeAbstract.isChecked()
        output_options = {
            "with_percent": with_percent,
            "sa_to_pie": sa_to_pie,
            "gen_abstract": gen_abstract,
            "with_emphasis": self.ui.checkBoxCellEmphasis.isChecked(),
            "reserved_names": [
                self.STRINGS.get("TOTAL", "TOTAL"),
                self.STRINGS.get("BLANK", "BLANK"),
                self.STRINGS.get("ERROR", "ERROR"),
            ],
            # raw output
            "raw_output": self.ui.checkBoxRaw.isChecked(),
        }

        self.simple_aggregation = SimpleAggregationObject(conf, QDir(filepath).filePath(self.tr('simple.xlsx')), output_options, strings=self.STRINGS)
        self.setProgressObject(self.simple_aggregation)
        self.simple_aggregation.finished.connect(self.simpleFinished)

        self.simple_aggregation.moveToThread(self.simple_thread)
        self.simple_thread.start()
        #self.simple_aggregation.aggregate()
        self.invoke_aggregate(self.simple_aggregation, conf, frame, dropna, aggregate_options)

    @pyqtSlot()
    def on_pushButtonCross_clicked(self):
        self.ui.pushButtonSimple.setEnabled(False)
        self.ui.pushButtonCross.setEnabled(False)
        dropna = self.ui.checkBoxDropNA.isChecked()
        aggregate_options = self.get_aggregate_options()
        try:
            conf, frame, filepath = self.loadSources(**aggregate_options)
        except LoadException:
            self.addMessage(self.tr('Error: config load failed.'))
            self.showMessageTab()
            return

        cross_table_format = self.crossEnums[self.ui.comboBoxCrossFormat.currentIndex()]
        with_percent = self.ui.checkBoxWithPercent.isChecked()
        drops = []
        if self.ui.checkBoxChartDropYBlank.isChecked():
            drops.append(self.STRINGS.get("BLANK", "BLANK"))
            if aggregate_options["aggregate_error"]:
                drops.append(self.STRINGS.get("ERROR", "ERROR"))
        output_options = {
            "cross_table_format": cross_table_format,
            "with_percent": with_percent,
            "with_emphasis": self.ui.checkBoxCellEmphasis.isChecked(),
            "reserved_names": [
                self.STRINGS.get("TOTAL", "TOTAL"),
                self.STRINGS.get("BLANK", "BLANK"),
                self.STRINGS.get("ERROR", "ERROR"),
            ],
            # chart option
            "chart": {
                "with_total": self.ui.checkBoxChartAddYTotal.isChecked(),
                "drops": drops,
            },
            # raw output
            "raw_output": self.ui.checkBoxRaw.isChecked(),
        }

        self.cross_aggregation = CrossAggregationObject(conf, QDir(filepath).filePath(self.tr('cross.xlsx')), output_options, strings=self.STRINGS)
        self.setProgressObject(self.cross_aggregation)
        self.cross_aggregation.finished.connect(self.crossFinished)
        self.cross_aggregation.moveToThread(self.cross_thread)
        self.cross_thread.start()
        #self.cross_aggregation.aggregate()
        self.invoke_aggregate(self.cross_aggregation, conf, frame, dropna, aggregate_options)

    def get_aggregate_options(self):
        extend_refs = self.ui.checkBoxExtendFilter.isChecked()
        aggregate_error = self.ui.checkBoxAggregateError.isChecked()
        return {
            "extend_refs": extend_refs,
            "aggregate_error": aggregate_error,
        }

    @pyqtSlot()
    def on_pushButtonExpand_clicked(self):
        try:
            conf, frame, filepath = self.loadSources()
        except LoadException:
            self.addMessage(self.tr('Error: config load failed.'))
            self.showMessageTab()
            return

        dest = pandas.DataFrame()
        self.ui.progressBar.setValue(0)
        self.progressInit(len(conf.columnOrder))
        for p, column in enumerate(conf.columnOrder, 1):
            self.ui.progressBar.setValue(p)
            columnConfig = conf.columns[column]
            if columnConfig.type not in [config.SINGLE, config.MULTIPLE]:
                dest[column] = frame[column]
                continue
            if columnConfig.type == config.SINGLE or len(columnConfig.choice) <= 1:
                dest[column] = frame[column]
            elif columnConfig.type == config.MULTIPLE:
                expanded = (
                    utils.expand_base(frame[column])
                        .apply(lambda x: pandas.Series(1, index=x))
                        .reindex(index=frame.index, columns=range(1, len(columnConfig.choice)+1))
                )
                for i, xcol in enumerate(expanded.columns, 1):
                    dest["{}-{}".format(column, i)] = expanded[xcol]
        dest.to_excel(str(QDir(filepath).filePath(self.tr('expand.xlsx'))))
        QMessageBox.information(self, self.tr('Finished'), self.tr('Finished.'))

    def loadSources(self, **kwargs):
        """
        :rtype: config.Config, pandas.DataFrame, str
        :kwargs:
          - :type aggregate_error: bool
        """
        # parameters
        aggregate_error = kwargs.get("aggregate_error", False)

        self.ui.progressBarGeneral.setValue(0)
        self.ui.progressBar.setValue(0)
        self.clearMessage()
        # load source
        with status.MainWindowStatus(self) as state:
            state.setMessage(self.tr("loading..."))
            inputFilePath = str(self.ui.lineEditInput.text())
            if not QFile.exists(inputFilePath):
                self.addMessage(self.tr('Error: Input "%1" not found.').arg(inputFilePath))
                raise LoadException()
            self.addMessage(self.tr('Input: "%1"').arg(inputFilePath))

            sheet_setting = qsource.Source.sheet_setting()
            sheet_cross = qsource.Source.sheet_cross()
            sheet_source = qsource.Source.sheet_source()
            try:
                frames = self.load_excel_sheets(inputFilePath, [
                    sheet_setting,
                    sheet_cross,
                    sheet_source,
                ])
            except:
                self.addMessage(self.tr('Error: Input "%1" load failed.').arg(inputFilePath))
                raise LoadException()

            def sheetNotFound(name):
                self.addMessage(self.tr('Error: Sheet "%1" is not found.').arg(name))

            no_error = True
            for name in [sheet_setting, sheet_cross, sheet_source]:
                if name not in frames:
                    sheetNotFound(name)
                    no_error = False
            if not no_error:
                raise LoadException()

            settingFrame = frames[sheet_setting]
            crossFrame = frames[sheet_cross]
            sourceFrame = frames[sheet_source]

            def invalidSource(name):
                self.addMessage(self.tr('Error: Sheet "%1" is invalid format.').arg(name))

            # check frame
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
                raise LoadException()

            # drop TITLE helper
            sourceFrame = sourceFrame.ix[1:]
            # drop ID NaN
            sourceFrame = sourceFrame[sourceFrame[qsource.Source.setting_id()].notnull()]

            TOTAL = self.STRINGS.get("TOTAL", "TOTAL")
            BLANK = self.STRINGS.get("BLANK", "BLANK")
            ERROR = self.STRINGS.get("ERROR", "ERROR")
            reserved_names = [TOTAL, BLANK, ERROR]

            cb = ConfigValidationObject(self)
            conf = config.makeConfigByDataFrame(settingFrame, crossFrame, cb, reserved=reserved_names)
            if cb.messages():
                self.addMessages(cb.messages())
                self.showMessageTab()
                QMessageBox.warning(self, self.tr("Warning"), self.tr("There is a problem with the configuration."))

            no_error = True
            # check filter validation
            for filter in conf.filters:
                if filter.key not in conf.columnOrder:
                    self.addMessage(self.tr('Error: filter key "%1" is not defined.').arg(filter.key))
                    no_error = False
            if not no_error:
                raise LoadException()

        self.ui.progressBarGeneral.setValue(1)

        ignoreForbidden = self.ui.checkBoxIgnoreForbiddenError.isChecked()
        # validation
        with status.MainWindowStatus(self) as state:
            state.setMessage(self.tr("validating..."))
            self.validator = qvalidator.QValidationObject(conf, self, noticeForbidden=(not ignoreForbidden))
            self.setProgressObject(self.validator)
            self.validator.finished.connect(self.validationFinished)
            self.validator.validate(sourceFrame)  # no threading
            if aggregate_error:
                sourceFrame = self.validator.errorToError(sourceFrame, ERROR)
            else:
                sourceFrame = self.validator.errorToNaN(sourceFrame)
            conf = self.validator.updateConfig(conf)

        self.ui.progressBarGeneral.setValue(2)

        outputFilePath = str(self.ui.lineEditOutput.text())
        if not QFileInfo(outputFilePath).isDir():
            self.addMessage(self.tr('Error: output file path is not directory.'))
            raise LoadException()

        return conf, sourceFrame, outputFilePath

    def load_excel_sheets(self, path, sheets):
        book = xlrd.open_workbook(path)
        names = book.sheet_names()
        size = len(book.sheets())
        temp = []
        for sheet in sheets:
            if ((isinstance(sheet, str) and sheet in names) or
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
        if not ret:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Write error.'))
            return
        if self.validation_error:
            self.showMessageTab()
            QMessageBox.warning(self, self.tr('Finished'), self.tr('Finished, but input data have errors.'))
            return
        QMessageBox.information(self, self.tr('Finished'), self.tr('Finished.'))

    @pyqtSlot()
    def crossFinished(self):
        self.cross_thread.exit(0)
        with BusyCursor(self):
            ret = self.cross_aggregation.save()
        self.ui.pushButtonSimple.setEnabled(True)
        self.ui.pushButtonCross.setEnabled(True)
        if not ret:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Write error.'))
            return
        if self.validation_error:
            self.showMessageTab()
            QMessageBox.warning(self, self.tr('Finished'), self.tr('Finished, but input data have errors.'))
            return
        QMessageBox.information(self, self.tr('Finished'), self.tr('Finished.'))

    @pyqtSlot(bool)
    def validationFinished(self, error):
        self.validation_error = error
        if error:
            self.model.setArray(self.model.array()+self.validator.messages)

    @pyqtSlot(str)
    def on_lineEditInput_textChanged(self, text):
        inputFilePath = str(self.ui.lineEditInput.text())
        outputFilePath = str(self.ui.lineEditOutput.text())
        # input existing & output empty
        if QFile.exists(inputFilePath) and not outputFilePath:
            self.ui.lineEditOutput.setText(QFileInfo(inputFilePath).dir().absolutePath())


class ConfigValidationObject(QObject, config.ConfigCallback):

    warning = pyqtSignal(str)

    DUPLICATED = 1

    def __init__(self, parent):
        """
        :type parent: QObject
        :param parent: parent object
        """
        super(ConfigValidationObject, self).__init__(parent)
        self.messages_ = []

    def duplicatedChoice(self, column):
        """
        :type column: str
        :param column: name of error column
        """
        self.messages_.append(self.tr('column "%1" has duplicate choices.').arg(column))

    def reservedChoice(self, column):
        """
        :type column: str
        :param column: name of error column
        """
        self.messages_.append(self.tr('column "%1" has reserved name.').arg(column))

    def messages(self):
        return self.messages_


class QSimpleAggregationAnalyzer(QObject, analyzer.SimpleAggregationAnalyzer):
    def __init__(self, reserved_names, parent=None):
        QObject.__init__(self, parent)
        analyzer.SimpleAggregationAnalyzer.__init__(self, reserved_names)

    def abstract(self, series):
        rs = self._abstract_info(series)
        max_count = 4
        count = 0
        abstracts = []
        for key in sorted(rs.keys(), reverse=True):
            names = rs[key]
            if count == 0 and len(names) == 1:
                # first special
                abstracts.append(str(self.tr('"%1" is %2%, it is most common').arg(names[0]).arg(key, 0, "f", 1)))
            else:
                # other
                secondary = ""
                if count == 1:
                    secondary = str(self.tr(u"secondary,"))
                indexes = str(self.tr(" ", "spacer")).join([str(self.tr(u'"%1"').arg(x)) for x in names])
                abstracts.append(str(self.tr(u'%1%2 is %3%').arg(secondary).arg(indexes).arg(key, 0, "f", 1)))
            count += len(names)
            if count >= max_count:
                break
        return str(self.tr(", ", "separator")).join(abstracts) + str(self.tr("Concluded."))


class SimpleAggregationObject(qaggregation.SimpleAggregationObject):
    def __init__(self, conf, filepath, options, strings, parent=None):
        super(SimpleAggregationObject, self).__init__(parent)
        self.config = conf
        self.filepath = filepath
        self.options = options
        self.strings = strings
        self.analyzer = QSimpleAggregationAnalyzer(reserved_names=self.strings)
        self.series = {}

    def addSeries(self, name, series):
        self.series[name] = series

    def save(self):
        # options
        with_percent = self.options.get("with_percent", False)
        sa_to_pie = self.options.get("sa_to_pie", False)
        gen_abstract = self.options.get("gen_abstract", False)
        with_emphasis = self.options.get("with_emphasis", False)
        reserved_names = self.options.get("reserved_names", [])

        if self.options.get("raw_output", False):
            root, ext = os.path.splitext(str(self.filepath))
            try:
                with open(root + ".pickle", "wb") as fp:
                    import pickle
                    pickle.dump({
                        "type": "simple",
                        #"config": self.config,
                        #"options": self.options,
                        "series": [{"dict": x.to_dict(), "index": x.index.tolist()} for x in self.series],
                    }, fp)
            except IOError:
                return False
            return True

        from . import excel
        book = excel.SurveyExcelBook(str(self.filepath), with_percent=with_percent, reserved_names=reserved_names)
        sheet = book.worksheet(str(self.tr('SimpleAggregation')))

        abstracts = []
        for column in self.config.columnOrder:
            if column not in self.series:
                continue
            current_config = self.config.columns.get(column, {})
            title = current_config.get('title', '')
            sheet.setTitle(title)
            to_pie = sa_to_pie and (current_config.get("type") == config.SINGLE)
            sheet.paste(self.series[column], to_pie=to_pie, with_emphasis=with_emphasis)
            if gen_abstract:
                abstracts.append((column, title, self.analyzer.abstract(self.series[column])))
            sheet.addPadding(3)

        if gen_abstract and abstracts:
            sheet = book.worksheet(str(self.tr("Comment")))
            for column, title, abstract in abstracts:
                sheet.write(0, 0, column)
                sheet.write(1, 0, title)
                sheet.write(2, 0, abstract)
                sheet.addPadding(4)

        try:
            book.close()
        except IOError:
            return False
        return True


class CrossAggregationObject(qaggregation.CrossAggregationObject):
    def __init__(self, conf, filepath, options, strings, parent=None):
        super(CrossAggregationObject, self).__init__(parent)
        self.config = conf
        self.filepath = filepath
        self.options = options
        self.strings = strings
        self.frames = {}

    def addDataFrame(self, key, target, frame):
        if target not in self.frames:
            self.frames[target] = {}
        self.frames[target][key] = frame

    def save(self):
        # options
        with_percent = self.options.get("with_percent", False)
        reserved_names = self.options.get("reserved_names", [])

        if self.options.get("raw_output", False):
            root, ext = os.path.splitext(str(self.filepath))
            try:
                with open(root + ".pickle", "wb") as fp:
                    import pickle
                    pickle.dump({
                        "type": "cross",
                        #"config": self.config,
                        #"options": self.options,
                        "frames": [{"dict": x.to_dict(), "index": x.index.tolist(), "columns": x.columns.tolist()} for x in self.frames],
                    }, fp)
            except IOError:
                return False
            return True

        # create workbook
        from . import excel
        book = excel.SurveyExcelBook(str(self.filepath), with_percent=with_percent, reserved_names=reserved_names)
        # get option
        names = []
        cross_table_format = self.options.get("cross_table_format", CrossFormat.Default)
        if cross_table_format == CrossFormat.SingleTable:
            book.SHEET = excel.CrossSingleTableSheet
        elif cross_table_format in [CrossFormat.Azemichi, CrossFormat.AzemichiAdvanced]:
            book.SHEET = excel.CrossAzemichiTableSheet

        # create sheets
        for target in self.config.cross.targets:
            # check id
            if target.id not in self.frames:
                continue
            # check unique sheet name & normalize name
            name = utils.normalizeSheetName((target.name if target.name else target.id))
            name = name[:31]
            if name.lower() in names:
                i = 1
                while True:
                    i += 1
                    num_size = len(str(i))
                    test_name = "{} ({})".format(name[:31-(num_size+3)], i)
                    if test_name.lower() not in names:
                        name = test_name
                        break
            names.append(name.lower())
            sheet = book.worksheet(name)
            sheet.setTitle(self.config.columns.get(target.id, {}).get('title', ''))
            sheet.addPadding(2)
            for key in self.config.cross.keys:
                if key.id not in self.frames[target.id]:
                    continue
                paste_option = {
                    "chart": self.options.get("chart", {}),
                    "with_emphasis": self.options.get("with_emphasis", False),
                }
                if cross_table_format in [CrossFormat.SingleTable, CrossFormat.Azemichi, CrossFormat.AzemichiAdvanced]:
                    if cross_table_format == CrossFormat.AzemichiAdvanced:
                        paste_option["skip_header"] = False
                        paste_option["skip_same_all"] = False
                    sheet.paste(self.frames[target.id][key.id], name=(key.name or key.id), strings=self.strings, **paste_option)
                else:
                    # Default
                    sheet.setTitle(self.config.columns.get(key.id, {}).get('title', ''))
                    sheet.paste(self.frames[target.id][key.id], strings=self.strings, **paste_option)
                    sheet.addPadding(2)
        try:
            book.close()
        except IOError:
            return False
        return True
