# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QMimeData, QUrl
from PyQt4.QtGui import QLineEdit, QDragEnterEvent, QDropEvent

from .. import events


def test_file_dd_filter_drop_event(qtbot):
    widget = QLineEdit()
    qtbot.addWidget(widget)

    mime = QMimeData()
    mime.setUrls([
        QUrl("file:///path/to/file"),
    ])
    action = Qt.CopyAction | Qt.MoveAction
    point = widget.rect().center()

    event = QDropEvent(point, action, mime, Qt.LeftButton, Qt.NoModifier)
    event.acceptProposedAction()

    event_filter = events.FileDragAndDropFilter()
    assert event_filter.eventFilter(widget, event)

    assert widget.text() == "/path/to/file"


def test_file_dd_filter_drag_enter_event(qtbot):
    widget = QLineEdit()
    qtbot.addWidget(widget)

    mime = QMimeData()
    mime.setUrls([
        QUrl("file:///path/to/file"),
    ])
    action = Qt.CopyAction | Qt.MoveAction
    point = widget.rect().center()

    event = QDragEnterEvent(point, action, mime, Qt.LeftButton, Qt.NoModifier)

    event_filter = events.FileDragAndDropFilter()
    assert event_filter.eventFilter(widget, event)

    assert event.isAccepted()
