# -*- coding: utf-8 -*-

import os

import pandas
import pytest
from pytestqt.qt_compat import QT_API

from .. import mainwindow


BASE_DIR = os.path.dirname(__file__)
XLSX_PATH = os.path.join(BASE_DIR, "test_data/data.xlsx")
CSV_PATH = os.path.join(BASE_DIR, "test_data/data.csv")


def check_dataframe(df):
    assert df.columns.tolist() == ["a", "b", "c"]
    assert df["a"].tolist() == [1, 4, 7]
    assert df.ix[0].tolist() == [1, 2, 3]


@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_openExcel_xlsx(qtbot):
    run_openExcel(qtbot, XLSX_PATH)

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_openExcel_csv(qtbot):
    run_openExcel(qtbot, CSV_PATH)

def run_openExcel(qtbot, filepath):
    win = mainwindow.MainWindow()
    qtbot.add_widget(win)
    df = win.openExcel(filepath)
    assert isinstance(df, pandas.DataFrame)
    check_dataframe(df)


def run_openFile(qtbot, filepath):
    win = mainwindow.MainWindow()
    qtbot.add_widget(win)
    win.openFile(filepath)
    # check loaded dataframe
    check_dataframe(win.originalFrame)
    # check model
    assert win.frameModel.dataFrame().equals(win.originalFrame)

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_openFile_xlsx(qtbot):
    run_openFile(qtbot, XLSX_PATH)

@pytest.mark.skipif("QT_API != 'pyqt4'")
def test_openFile_xlsx(qtbot):
    run_openFile(qtbot, CSV_PATH)



