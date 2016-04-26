#! /usr/bin/env bash

pyuic4 src/generator/ui_mainwindow.ui -o src/generator/ui_mainwindow.py
pyuic4 src/generator/ui_columndialog.ui -o src/generator/ui_columndialog.py
pyuic4 src/generator/ui_datarangedialog.ui -o src/generator/ui_datarangedialog.py
pyrcc4 generator.qrc -o generator_rc.py
