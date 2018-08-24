#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from PyQt5.Qt import *


def main(argv):
    app = QApplication(argv)

    qtTr = QTranslator()
    if qtTr.load("qt_" + QLocale.system().name(), ':/i18n'):
        app.installTranslator(qtTr)

    liteTr = QTranslator()
    if liteTr.load("generator_" + QLocale.system().name(), ':/i18n'):
        app.installTranslator(liteTr)

    from src.generator.mainwindow import MainWindow

    win = MainWindow()
    win.show()

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
