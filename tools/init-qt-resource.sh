#! /usr/bin/env bash

pyuic5 src/ui_mainwindow.ui -o src/ui_mainwindow.py
pyrcc5 qsurveytools.qrc -o qsurveytools_rc.py
