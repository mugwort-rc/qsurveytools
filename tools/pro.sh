#! /usr/bin/env bash

pyuic5 src/pro/ui_configdialog.ui -o src/pro/ui_configdialog.py
pyuic5 src/pro/ui_crossconfigdialog.ui -o src/pro/ui_crossconfigdialog.py
pyuic5 src/pro/ui_crosstabdialog.ui -o src/pro/ui_crosstabdialog.py
pyuic5 src/pro/ui_filterconfigdialog.ui -o src/pro/ui_filterconfigdialog.py
pyuic5 src/pro/ui_listdialog.ui -o src/pro/ui_listdialog.py
pyuic5 src/pro/ui_sourceinfodialog.ui -o src/pro/ui_sourceinfodialog.py
pyuic5 src/pro/ui_surveydialog.ui -o src/pro/ui_surveydialog.py
pyuic5 src/pro/ui_tabledialog.ui -o src/pro/ui_tabledialog.py
pyuic5 src/pro/ui_mainwindow.ui -o src/pro/ui_mainwindow.py
pyrcc5 src/pro/resources.qrc -o src/pro/resources_rc.py
