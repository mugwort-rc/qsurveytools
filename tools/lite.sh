#! /usr/bin/env bash

pyuic4 src/lite/ui_mainwindow.ui -o src/lite/ui_mainwindow.py
pyrcc4 lite.qrc -o lite_rc.py
