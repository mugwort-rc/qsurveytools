# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtGui

class AutoCursor(object):
    """
    オートカーソル
    """
    def __init__(self, widget, shape):
        """
        :Parameters:
        - `widget`: 変更対象のウィジェット
        - `shape`: 変更するカーソル形
        """
        super(AutoCursor, self).__init__()
        self.widget = widget
        self.shape = shape

    def __enter__(self):
        """
        with構文に入った際にカーソルを設定する
        """
        self.old_cursor = self.widget.cursor()
        self.new_cursor = QtGui.QCursor(self.shape)
        self.widget.setCursor(self.new_cursor)
        return self

    def __exit__(self, type, value, traceback):
        """
        with構文を抜けた際に元のカーソルに戻す
        
        :Parameters:
        - `type`: excepted type
        - `value`: excepted value
        - `traceback`: excepted traceback
        """
        self.widget.setCursor(self.old_cursor)
        return type is None

    def setShape(self, shape):
        """
        withステートメント上のカーソル形を設定する
        
        :Parameters:
        - `shape`: カーソル形
        """
        self.new_cursor = QtGui.QCursor(shape)
        self.widget.setCursor(self.new_cursor)

    def setArrow(self):
        """
        デフォルトのカーソルにする
        """
        self.setShape(QtCore.Qt.ArrowCursor)

    def setWait(self):
        """
        ウェイトカーソルにする
        """
        self.setShape(QtCore.Qt.WaitCursor)

    def setBusy(self):
        """
        ビジーカーソルにする
        """
        self.setShape(QtCore.Qt.BusyCursor)

class BusyCursor(AutoCursor):
    """
    デフォルトがビジー状態のオートカーソル
    """
    def __init__(self, widget):
        super(BusyCursor, self).__init__(widget, QtCore.Qt.BusyCursor)

class WaitCursor(AutoCursor):
    """
    デフォルトがウェイト状態のオートカーソル
    """
    def __init__(self, widget):
        super(WaitCursor, self).__init__(widget, QtCore.Qt.WaitCursor)

