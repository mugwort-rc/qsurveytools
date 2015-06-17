# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot, QObject

from .. import progress


def test_progress(qtbot):
    class TestProgress(progress.ProgressObject):
        def run(self, maximum):
            self.initialized.emit(maximum)
            for i in range(1, maximum+1):
                self.updated.emit(i)
            self.finished.emit()

    class TestSlot(QObject):
        def __init__(self, parent=None):
            super(TestSlot, self).__init__(parent)
            self.initialized_called = False
            self.updated_called = False
            self.finished_called = False
            self.initialized_count = 0
            self.updated_count = 0
            self.finished_count = 0
            self.maximum = 0
            self.value = 0

        @pyqtSlot(int)
        def initialized(self, maximum):
            self.initialized_called = True
            self.initialized_count += 1
            self.maximum = maximum

        @pyqtSlot(int)
        def updated(self, value):
            self.updated_called = True
            self.updated_count += 1
            self.value = value

        @pyqtSlot()
        def finished(self):
            self.finished_called = True
            self.finished_count += 1

    slots = TestSlot()
    prog = TestProgress()
    prog.initialized.connect(slots.initialized)
    prog.updated.connect(slots.updated)
    prog.finished.connect(slots.finished)

    with qtbot.waitSignal(prog.finished, timeout=1000) as blocker:
        prog.run(10)

    assert slots.initialized_called
    assert slots.updated_called
    assert slots.finished_called
    assert slots.initialized_count == 1
    assert slots.updated_count == 10
    assert slots.finished_count == 1
    assert slots.maximum == 10
    assert slots.value == 10
