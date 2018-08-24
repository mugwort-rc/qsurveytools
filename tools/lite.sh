#! /usr/bin/env bash

pyuic5 src/lite/ui_mainwindow.ui -o src/lite/ui_mainwindow.py
pyrcc5 lite.qrc -o lite_rc.py
