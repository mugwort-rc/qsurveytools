# -*- coding: utf-8 -*-

from PyQt5.QtCore import pyqtSignal, QObject


class ProgressObject(QObject):

    initialized = pyqtSignal(int)
    updated = pyqtSignal(int)
    finished = pyqtSignal()
