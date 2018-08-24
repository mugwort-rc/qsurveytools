#! /usr/bin/env bash

pyuic5 src/condition/ui_conditiondialog.ui -o src/condition/ui_conditiondialog.py
pyuic5 src/condition/ui_mainwindow.ui -o src/condition/ui_mainwindow.py
pyrcc5 condition.qrc -o condition_rc.py
