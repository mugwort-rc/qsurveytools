#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

from PyQt5.Qt import *


import qsurveytools_rc


def main(argv):
    app = QApplication(argv)

    splash = None
    pixmap = QPixmap(':/img/splashscreen.png')
    splash = QSplashScreen(pixmap)
    splash.show()

    qtTr = QTranslator()
    if qtTr.load("qt_" + QLocale.system().name(), ':/i18n'):
        app.installTranslator(qtTr)

    liteTr = QTranslator()
    if liteTr.load("lite_" + QLocale.system().name(), ':/i18n'):
        app.installTranslator(liteTr)

    from src.mainwindow import MainWindow

    win = MainWindow()
    win.show()

    if splash is not None:
        splash.finish(win)

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
