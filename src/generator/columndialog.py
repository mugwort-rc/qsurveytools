# -*- coding: utf-8 -*-

from PyQt5.Qt import *

from .ui_columndialog import Ui_ColumnDialog


class ColumnDialog(QDialog):
    def __init__(self, parent=None):
        super(ColumnDialog, self).__init__(parent)
        self.ui = Ui_ColumnDialog()
        self.ui.setupUi(self)
