# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from PyQt5.Qt import *

from .ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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
