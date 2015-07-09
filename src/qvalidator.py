# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QApplication

import progress
import validator


class QValidationObject(progress.ProgressObject, validator.ValidationCallback):

    finished = pyqtSignal(bool)

    def __init__(self, parent=None):
        """
        :type parent: QObject
        """
        super(QValidationObject, self).__init__(parent)
        self.messages = []
        self.error = False

    def initialize(self, maximum):
        """
        :type maximum: int
        :param maximum: maximum of progress
        """
        self.initialized.emit(maximum)

    def update(self, current):
        """
        :type current: int
        :param current: current value of progress
        """
        self.updated.emit(current)

    def finish(self):
        self.finished.emit(self.error)

    def columnNotFound(self, column):
        self.messages.append(
            QApplication.translate("QValidationObject", "Warning: Column \"%1\" is not found.")
                    .arg(column)
        )
        self.error = True

    def settingNotFound(self, column):
        self.messages.append(
            QApplication.translate("QValidationObject", "Warning: Setting \"%1\" is not found.")
                    .arg(column)
        )
        self.error = True

    def settingIsUnknown(self, column):
        self.messages.append(
            QApplication.translate("QValidationObject", "Warning: Setting \"%1\" is Unknown type.")
                    .arg(column)
        )
        self.error = True

    def validationError(self, column, row, value, **kwargs):
        row = row if kwargs.get("id") is None else kwargs.get("id")
        self.messages.append(
            QApplication.translate("QValidationObject", 'Warning: Undefined value found in "%1" - #%2 : \'%3\'')
                    .arg(column)
                    .arg(row)
                    .arg(value)
        )
        self.error = True

    def multipleExceptionError(self, column, row, value, **kwargs):
        row = row if kwargs.get("id") is None else kwargs.get("id")
        self.messages.append(
            QApplication.translate("QValidationObject", 'Warning: Multiple exception error found in "%1" - #%2 : \'%3\'')
                    .arg(column)
                    .arg(row)
                    .arg(value)
        )
        self.error = True

    def limitationError(self, column, row, value, **kwargs):
        row = row if kwargs.get("id") is None else kwargs.get("id")
        self.messages.append(
            QApplication.translate("QValidationObject", 'Warning: It exceeds the limit value was found in "%1" - #%2 : \'%3\'')
                    .arg(column)
                    .arg(row)
                    .arg(value)
        )
        self.error = True

    def validate(self, conf, frame):
        impl = validator.ValidationObject(self, conf)
        impl.validate(frame)
