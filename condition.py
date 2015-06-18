#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from PyQt4.Qt import *

from src.condition.mainwindow import MainWindow

def main(args):
    app = QApplication(args)

    win = MainWindow()
    win.show()

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main(sys.argv))