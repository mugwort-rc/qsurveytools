# -*- coding: utf-8 -*-

# python2 compatibility
_str = str
str = unicode

import os
from decimal import Decimal

from jinja2 import Environment, FileSystemLoader
import pandas

from PyQt4.Qt import *
from PyQt4.QtWebKit import *

from models import DataFrameTableModel
from models import SeriesTableModel

from ui_surveydialog import Ui_SurveyDialog

BASEPATH = os.path.abspath(os.path.dirname(__file__))

def customRound(x, y):
    if pandas.np.isnan(x):
        return pandas.np.nan
    return str(round(Decimal(float(x)), y))

class SurveyDialog(QDialog):
    def __init__(self, parent=None):
        super(SurveyDialog, self).__init__(parent)
        self.ui = Ui_SurveyDialog()
        self.ui.setupUi(self)

class SimpleSurveyDialog(SurveyDialog):
    def __init__(self, parent=None):
        super(SimpleSurveyDialog, self).__init__(parent)
        self.series = []

        self.TOTAL_STR = self.tr('TOTAL')
        self.P_STR = self.tr('P')
        self.R_STR = self.tr('R')

    def addSeries(self, name, series):
        self.series.append((name, series))

    def addModel(self, name, model):
        widget = QTableView(self)
        widget.setModel(model)
        self.ui.tabWidget.addTab(widget, name)

    def buildReport(self):
        TOTAL = str(self.TOTAL_STR)
        P = str(self.P_STR)
        R = str(self.R_STR)
        env = Environment(loader=FileSystemLoader(os.path.join(BASEPATH, 'templates')))
        tpl = env.get_template('simple.html')
        reports = []
        for name, series in self.series:
            frame = series.to_frame()
            frame.columns = [P]
            if series.index[0] == TOTAL and not pandas.np.isnan(series[TOTAL]):
                total = float(series[TOTAL])
                frame[R] = series.apply(lambda x: x/total*100).apply(lambda x: customRound(x, 1))
            else:
                frame[R] = pandas.Series()
            reports.append({
                'name': name,
                'table': frame.to_html(classes=('table',), na_rep=''),
            })
        html = tpl.render({
            'reports': reports,
        })
        view = QWebView(self)
        view.setHtml(html)
        self.ui.tabWidget.addTab(view, self.tr('Report'))

    def open(self):
        self.buildReport()
        # build tabs
        for name, series in self.series:
            model = SeriesTableModel(self)
            model.setSeries(series)
            self.addModel(name, model)
        super(SimpleSurveyDialog, self).open()

class CrossSurveyDialog(SurveyDialog):
    def __init__(self, parent=None):
        super(CrossSurveyDialog, self).__init__(parent)
        self.dataFrames = []
        self.targets = []
        self.reports = {}
        self.widgets = {}

    def addDataFrame(self, key, target, frame):
        self.dataFrames.append((key, target, frame))

    def addTarget(self, target):
        if target in self.widgets:
            return
        widget = QTabWidget(self)
        widget.addTab(self.reports[target], self.tr('Report'))
        self.widgets[target] = widget
        self.ui.tabWidget.addTab(widget, target)

    def addModel(self, key, target, model):
        if target not in self.widgets:
            self.addTarget(target)
        tabWidget = self.widgets[target]
        widget = QTableView(self)
        widget.setModel(model)
        tabWidget.addTab(widget, key)

    def setTargets(self, targets):
        self.targets = targets

    def buildReport(self):
        TOTAL = 'All'
        env = Environment(loader=FileSystemLoader(os.path.join(BASEPATH, 'templates')))
        tpl = env.get_template('cross.html')
        reports = {t:[] for k,t,f in self.dataFrames}
        for key, target, frame in self.dataFrames:
            if frame.columns[0] == TOTAL and not pandas.np.isnan(frame[TOTAL][TOTAL]):
                rframe = frame.apply(lambda x: x/frame[TOTAL].apply(float)*100).apply(lambda x: x.apply(lambda y: customRound(y, 1)))
            else:
                rframe = pandas.DataFrame(index=frame.index, columns=frame.columns)
            reports[target].append({
                'name': key,
                'table': frame.to_html(classes=('table',), na_rep=''),
                'rtable': rframe.to_html(classes=('table',), na_rep=''),
            })

        for target in self.targets:
            if target not in reports:
                continue
            html = tpl.render({
                'target': target,
                'reports': reports[target],
            })
            view = QWebView(self)
            view.setHtml(html)
            self.reports[target] = view

    def open(self):
        self.buildReport()
        # build tabs
        for key, target, frame in self.dataFrames:
            model = DataFrameTableModel(self)
            model.setDataFrame(frame)
            self.addModel(key, target, model)
        super(CrossSurveyDialog, self).open()
