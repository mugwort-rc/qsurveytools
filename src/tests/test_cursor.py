# -*- coding: utf-8 -*-

import pytest
from pytestqt.qt_compat import QT_API

if QT_API == 'pyqt4':
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QWidget, QCursor
elif QT_API == 'pyqt5':
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QCursor
    from PyQt5.QtWidgets import QWidget

from .. import cursor


def test_AutoCursor(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    c = cursor.AutoCursor(widget, Qt.BusyCursor)
    assert c.widget == widget
    assert c.shape == Qt.BusyCursor

    assert widget.cursor().shape() == Qt.ArrowCursor
    with c:
        assert widget.cursor().shape() == Qt.BusyCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_BusyCursor(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    c = cursor.BusyCursor(widget)
    assert c.widget == widget
    assert c.shape == Qt.BusyCursor

    assert widget.cursor().shape() == Qt.ArrowCursor
    with c:
        assert widget.cursor().shape() == Qt.BusyCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_WaitCursor(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    c = cursor.WaitCursor(widget)
    assert c.widget == widget
    assert c.shape == Qt.WaitCursor

    assert widget.cursor().shape() == Qt.ArrowCursor
    with c:
        assert widget.cursor().shape() == Qt.WaitCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_default(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    widget.setCursor(QCursor(Qt.UpArrowCursor))
    assert widget.cursor().shape() == Qt.UpArrowCursor
    with cursor.BusyCursor(widget):
        widget.cursor().shape() == Qt.BusyCursor
    assert widget.cursor().shape() == Qt.UpArrowCursor


def test_multiplex(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    assert widget.cursor().shape() == Qt.ArrowCursor
    with cursor.BusyCursor(widget):
        assert widget.cursor().shape() == Qt.BusyCursor
        with cursor.WaitCursor(widget):
            assert widget.cursor().shape() == Qt.WaitCursor
        assert widget.cursor().shape() == Qt.BusyCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_change(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    assert widget.cursor().shape() == Qt.ArrowCursor
    with cursor.BusyCursor(widget):
        assert widget.cursor().shape() == Qt.BusyCursor
        widget.setCursor(QCursor(Qt.WaitCursor))
        assert widget.cursor().shape() == Qt.WaitCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_with_as(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    assert widget.cursor().shape() == Qt.ArrowCursor
    with cursor.BusyCursor(widget) as c:
        assert isinstance(c, cursor.AutoCursor)
        assert widget.cursor().shape() == Qt.BusyCursor
        c.setShape(Qt.WaitCursor)
        assert widget.cursor().shape() == Qt.WaitCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_set_arrow(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    assert widget.cursor().shape() == Qt.ArrowCursor
    with cursor.BusyCursor(widget) as c:
        assert isinstance(c, cursor.AutoCursor)
        assert widget.cursor().shape() == Qt.BusyCursor
        c.setArrow()
        assert widget.cursor().shape() == Qt.ArrowCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_set_busy(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    assert widget.cursor().shape() == Qt.ArrowCursor
    with cursor.WaitCursor(widget) as c:
        assert isinstance(c, cursor.AutoCursor)
        assert widget.cursor().shape() == Qt.WaitCursor
        c.setBusy()
        assert widget.cursor().shape() == Qt.BusyCursor
    assert widget.cursor().shape() == Qt.ArrowCursor


def test_set_wait(qtbot):
    widget = QWidget()
    qtbot.add_widget(widget)

    assert widget.cursor().shape() == Qt.ArrowCursor
    with cursor.BusyCursor(widget) as c:
        assert isinstance(c, cursor.AutoCursor)
        assert widget.cursor().shape() == Qt.BusyCursor
        c.setWait()
        assert widget.cursor().shape() == Qt.WaitCursor
    assert widget.cursor().shape() == Qt.ArrowCursor
