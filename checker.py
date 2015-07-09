#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.Qt import *

from src.checker.mainwindow import MainWindow

def main(args):
    app = QApplication(args)

    qtTr = QTranslator()
    if qtTr.load("qt_" + QLocale.system().name(), ":/i18n/"):
        app.installTranslator(qtTr)

    appTr = QTranslator()
    if appTr.load("checker_" + QLocale.system().name(), ":/i18n/"):
        app.installTranslator(appTr)

    win = MainWindow()
    win.show()

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main(sys.argv))