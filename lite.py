#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from PyQt4.Qt import *

def main():
    app = QApplication(sys.argv)

    qtTr = QTranslator()
    if qtTr.load("qt_" + QLocale.system().name(), './.config/i18n'):
        app.installTranslator(qtTr)

    liteTr = QTranslator()
    if liteTr.load("lite_" + QLocale.system().name(), './.config/i18n'):
        app.installTranslator(liteTr)

    splash = None
    splashpath = QApplication.translate('main', './.config/splashscreen.png')
    if os.path.exists(str(splashpath)):
        pixmap = QPixmap(splashpath)
        splash = QSplashScreen(pixmap)
        splash.show()

    from src.lite.mainwindow import MainWindow
    win = MainWindow()
    win.show()
    if splash is not None:
        splash.finish(win)

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
