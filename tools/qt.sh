#! /usr/bin/env bash

pyuic4 src/lite/ui_mainwindow.ui -o src/lite/ui_mainwindow.py

pyuic4 src/pro/ui_configdialog.ui -o src/pro/ui_configdialog.py
pyuic4 src/pro/ui_crossconfigdialog.ui -o src/pro/ui_crossconfigdialog.py
pyuic4 src/pro/ui_crosstabdialog.ui -o src/pro/ui_crosstabdialog.py
pyuic4 src/pro/ui_filterconfigdialog.ui -o src/pro/ui_filterconfigdialog.py
pyuic4 src/pro/ui_listdialog.ui -o src/pro/ui_listdialog.py
pyuic4 src/pro/ui_sourceinfodialog.ui -o src/pro/ui_sourceinfodialog.py
pyuic4 src/pro/ui_surveydialog.ui -o src/pro/ui_surveydialog.py
pyuic4 src/pro/ui_tabledialog.ui -o src/pro/ui_tabledialog.py
pyuic4 src/pro/ui_mainwindow.ui -o src/pro/ui_mainwindow.py
pyrcc4 src/pro/resources.qrc -o src/pro/resources_rc.py
