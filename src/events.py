# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, QEvent


class FileDragAndDropFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            mimeData = event.mimeData()
            if mimeData.hasUrls() and len(mimeData.urls()) == 1 and mimeData.urls()[0].isLocalFile():
                event.accept()
            else:
                event.ignore()
            return True
        elif event.type() == QEvent.Drop:
            mimeData = event.mimeData()
            if mimeData.hasUrls() and len(mimeData.urls()) == 1 and mimeData.urls()[0].isLocalFile():
                obj.setText(mimeData.urls()[0].toLocalFile())
            return True
        return super(FileDragAndDropFilter, self).eventFilter(obj, event)
