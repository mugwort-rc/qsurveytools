#! /usr/bin/env bash

pyuic4 src/condition/ui_conditiondialog.ui -o src/condition/ui_conditiondialog.py
pyuic4 src/condition/ui_mainwindow.ui -o src/condition/ui_mainwindow.py
pyrcc4 condition.qrc -o condition_rc.py
