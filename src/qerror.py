# -*- coding: utf-8 -*-

from PyQt4.Qt import *

from . import error
from . import models


class ErrorContext(error.ErrorContext):
    def __init__(self, parent):
        """
        :type parent: QObject
        :param parent: parent object
        """
        super(ErrorContext, self).__init__()
        self.model_ = models.ArrayListModel(parent)

    @pyqtSlot(QString)
    def addMessage(self, message):
        """
        :type message: QString
        """
        current = self.model_.array()
        self.addError(len(current))
        self.model_.setArray(current+[message])

    @pyqtSlot(QStringList)
    def addMessages(self, messages):
        """
        :type message: QStringList
        """
        current = self.model_.array()
        size = len(current)
        for i in range(len(messages)):
            self.addError(size + i)
        self.model_.setArray(current+messages)

    @pyqtSlot()
    def clearMessage(self):
        self.model_.setArray([])

    def clear(self):
        super(ErrorContext, self).clear()
        self.clearMessage()

    def model(self):
        """
        :rtype: models.ArrayListModel
        """
        return self.model_


class SurveyErrorContext(ErrorContext):

    LOAD = 1
    PARSE = 2
    VALIDATE = 3

    def setLoading(self):
        self.setContext(self.LOAD)

    def setParsing(self):
        self.setContext(self.PARSE)

    def setValidating(self):
        self.setContext(self.VALIDATE)
