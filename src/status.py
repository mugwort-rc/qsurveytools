# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject


class Status(QObject):
    def __init__(self, statusbar, parent=None):
        super(Status, self).__init__(parent)
        self.statusbar = statusbar

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.clearMessage()

    def clearMessage(self):
        self.statusbar.clearMessage()

    def setMessage(self, message, timeout=0):
        self.statusbar.showMessage(message, timeout)


class MainWindowStatus(Status):
    def __init__(self, window, parent=None):
        super(MainWindowStatus, self).__init__(window.statusBar(), parent)
