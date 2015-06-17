# -*- coding: utf-8 -*-

import os
import pandas

from PyQt4.Qt import *

from ui_sourceinfodialog import Ui_SourceInfoDialog

# python2 compatibility
str = unicode

class SourceInfoDialog(QDialog):
    def __init__(self, parent=None):
        super(SourceInfoDialog, self).__init__(parent)

        self.ui = Ui_SourceInfoDialog()
        self.ui.setupUi(self)

        self.SOURCE_FILTER = self.tr('Excel (*.xlsx);;CSV (*.csv)')

    def getOpenFileName(self, filter, caption='', dir=''):
        return QFileDialog.getOpenFileName(self, caption, dir, filter)

    def header(self):
        if not self.ui.checkBoxHeader.isChecked():
            return None
        return self.ui.spinBoxHeader.value()

    def index_col(self):
        if not self.ui.checkBoxHeader.isChecked():
            return None
        return self.ui.spinBoxID.value()

    def na_values(self):
        text = self.ui.plainTextEditNaValues.toPlainText().trimmed()
        if text.isEmpty():
            return None
        return map(str, text.split(QRegExp(r'\r?\n')))

    def filePath(self):
        return self.ui.lineEditFilepath.text()

    def setFilePath(self, filepath):
        self.ui.lineEditFilepath.setText(filepath)
        info = QFileInfo(filepath)
        filepath = str(filepath)
        if not os.path.exists(filepath):
            return
        df = None
        if info.suffix() == 'xlsx':
            df = pandas.read_excel(filepath, header=None, sheetname=0)
        elif info.suffix() == 'csv':
            df = pandas.read_csv(filepath, header=None)
        if df is None:
            return
        self.ui.spinBoxHeader.setMaximum(len(df.index)-1)
        self.ui.spinBoxID.setMaximum(len(df.columns)-1)

    @pyqtSlot()
    def on_toolButtonFilepath_clicked(self):
        filepath = self.getOpenFileName(self.SOURCE_FILTER)
        if filepath.isEmpty():
            return
        self.setFilePath(filepath)
