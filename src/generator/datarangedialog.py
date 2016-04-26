# -*- coding: utf-8 -*-

from PyQt4.Qt import *

from ui_datarangedialog import Ui_DataRangeDialog


class DataRangeDialog(QDialog):
    def __init__(self, parent=None):
        super(DataRangeDialog, self).__init__(parent)
        self.ui = Ui_DataRangeDialog()
        self.ui.setupUi(self)
