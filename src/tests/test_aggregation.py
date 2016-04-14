# -*- coding: utf-8 -*-

import os.path

import mock
import numpy
import pandas
import yaml

from .. import aggregation
from .. import config

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "test_data/config.yml")
CONFIG = yaml.load(open(CONFIG_PATH).read())


def test_simple_aggregation_callback_add_dataframe(capsys):
    cb = aggregation.SimpleAggregationCallback()
    assert isinstance(cb, aggregation.AggregationCallback)
    cb.addDataFrame(None, None)
    out, err = capsys.readouterr()
    assert err == "Warning: SimpleAggregationCallback does not implement addDataFrame()\n"

def test_cross_aggregation_callback_add_series(capsys):
    cb = aggregation.CrossAggregationCallback()
    assert isinstance(cb, aggregation.AggregationCallback)
    cb.addSeries(None, None)
    out, err = capsys.readouterr()
    assert err == "Warning: CrossAggregationCallback does not implement addSeries()\n"


def test_aggregation_object_filtered_frame():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    obj = aggregation.AggregationObject(cb, conf)

    frame = pandas.DataFrame([
        [1, "1,2", 1],
        [2, "1,3", 1],
        [3, "3", 1],
        [4, "1,2,3", 1],
    ], columns=["Q1", "Q2", "3"])

    filtered = obj.filteredFrame(frame, ["Q2"])
    assert len(filtered) == 3
    filtered = obj.filteredFrame(frame, ["3"])
    assert len(filtered) == 2
    filtered = obj.filteredFrame(frame, ["Q1", "Q2", "3"])
    assert len(filtered) == 2
    filtered = obj.filteredFrame(frame, [])
    assert len(filtered) == 4
    assert filtered.equals(frame)
    filtered = obj.filteredFrame(frame, ["hoge", "fuga", "piyo"])
    assert len(filtered) == 4
    assert filtered.equals(frame)


def test_aggregation_object_reindex():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    obj = aggregation.AggregationObject(cb, conf)

    series = pandas.Series([1, 2, 3, 4], index=[1, 2, 3, 4])
    ret = obj.reindex(series, "Q1", "index")
    assert ret.index.tolist() == ["a", "b", "c", "d"]
    assert ret.values.tolist() == [1, 2, 3, 4]
    assert series.index.tolist() == [1, 2, 3, 4]
    assert series.values.tolist() == [1, 2, 3, 4]


def test_aggregation_object_reindex_prefix_suffix():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    obj = aggregation.AggregationObject(cb, conf)

    series = pandas.Series([1, 2, 3, 4], index=[1, 2, 3, 4])
    ret = obj.reindex(series, "Q1", "index", prefix=["TOTAL"], suffix=["BLANK"])
    assert ret.index.tolist() == ["TOTAL", "a", "b", "c", "d", "BLANK"]
    assert ret.values.tolist()[1:-1] == [1, 2, 3, 4]
    assert numpy.isnan(ret.values.tolist()[0])
    assert numpy.isnan(ret.values.tolist()[-1])
    assert series.index.tolist() == [1, 2, 3, 4]
    assert series.values.tolist() == [1, 2, 3, 4]


def test_aggregation_object_reindex_with_error():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    obj = aggregation.AggregationObject(cb, conf)

    series = pandas.Series([1, 2, 3, 4], index=[0, 1, 2, 3])
    ret = obj.reindex(series, "Q1", "index")
    assert ret.index.tolist() == ["a", "b", "c", "d", 0]
    assert ret.values.tolist()[:-2] == [2, 3, 4]
    assert numpy.isnan(ret.values.tolist()[-2])
    assert ret.values.tolist()[-1] == 1
    assert series.index.tolist() == [0, 1, 2, 3]
    assert series.values.tolist() == [1, 2, 3, 4]


def test_simple_aggregation_object():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    obj = aggregation.SimpleAggregationObject(cb, conf)

    # Q1     Q2     Q3
    # T: 13  T: 10  T: 8
    # 1:  1  1:  6  1: 2
    # 2:  4  2:  5  2: 3
    # 3:  5  3:  7  3: 3
    # 4:  3
    frame = pandas.DataFrame(columns=["Q1", "Q2", "3"], data=[
        [1, "1,3", 3],
        [2, "1,2", 2],
        [3, "1,2,3", 1],
        [4, 1, 3],
        [2, 2, 2],
        [2, 3, 1],
        [3, 1, 3],
        [4, 2, 2],
        [3, "1,3", 1],
        [2, "1,2,3", 3],
        [3, "2,3", 2],
        [4, 3, 1],
        [3, 3, 3],
    ])
    vc = obj.value_counts(frame, "Q1")
    assert isinstance(vc, pandas.Series)
    # vc.values == [13, 1, 4, 5, 3, nan]
    assert vc.values.tolist()[:-1] == [13, 1, 4, 5, 3]
    assert numpy.isnan(vc.values.tolist()[-1])
    assert vc.index.tolist() == ["TOTAL", "a", "b", "c", "d", "BLANK"]

    vc = obj.value_counts(frame, "Q2")
    assert isinstance(vc, pandas.Series)
    # vc.values == [10, 6, 5, 7, nan]
    assert vc.values.tolist()[:-1] == [10, 6, 5, 7]
    assert numpy.isnan(vc.values.tolist()[-1])
    assert vc.index.tolist() == ["TOTAL", "x", "y", "z", "BLANK"]

    vc = obj.value_counts(frame, "3")
    assert isinstance(vc, pandas.Series)
    # vc.values == [8, 2, 3, 3]
    assert vc.values.tolist() == [8, 2, 3, 3]
    assert vc.index.tolist() == ["TOTAL", "1", "2", "3"]

    # test the not existing column
    vc = obj.value_counts(frame, "not existing")
    assert isinstance(vc, pandas.Series)
    values = vc.values.tolist()
    assert len(values) == 2
    assert numpy.isnan(values[0])
    assert numpy.isnan(values[1])

def test_simple_aggregation_object_with_dropna():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    obj = aggregation.SimpleAggregationObject(cb, conf, dropna=True)

    # Q1     Q2     Q3
    # T: 13  T: 9  T: 7
    # 1:  1  1:  5  1: 2
    # 2:  4  2:  5  2: 3
    # 3:  5  3:  7  3: 2
    # 4:  3
    frame = pandas.DataFrame(columns=["Q1", "Q2", "3"], data=[
        [1, "1,3", 3],
        [2, "1,2", 2],
        [3, "1,2,3", 1],
        [4, 1, 3],
        [2, 2, 2],
        [2, 3, 1],
        [3, None, 3],
        [4, 2, 2],
        [3, "1,3", 1],
        [2, "1,2,3", 3],
        [3, "2,3", 2],
        [4, 3, 1],
        [3, 3, 3],
    ])
    vc = obj.value_counts(frame, "Q1")
    assert isinstance(vc, pandas.Series)
    assert vc.values.tolist() == [13, 1, 4, 5, 3]
    assert vc.index.tolist() == ["TOTAL", "a", "b", "c", "d"]

    vc = obj.value_counts(frame, "Q2")
    assert isinstance(vc, pandas.Series)
    assert vc.values.tolist() == [9, 5, 5, 7]
    assert vc.index.tolist() == ["TOTAL", "x", "y", "z"]

    vc = obj.value_counts(frame, "3")
    assert isinstance(vc, pandas.Series)
    assert vc.values.tolist() == [7, 2, 3, 2]
    assert vc.index.tolist() == ["TOTAL", "1", "2", "3"]

    # test the not existing column
    vc = obj.value_counts(frame, "not existing")
    assert isinstance(vc, pandas.Series)
    values = vc.values.tolist()
    assert len(values) == 1
    assert numpy.isnan(values[0])

def test_simple_aggregation_object_with_callback():
    class TestCallback(aggregation.SimpleAggregationObject):

        initialize = mock.MagicMock(name="initialize")
        update = mock.MagicMock(name="update")
        finish = mock.MagicMock(name="finish")

        def __init__(self):
            self.series = []

        def addSeries(self, column, series):
            self.series.append((column, series))
    cb = TestCallback()
    conf = config.Config(CONFIG)
    obj = aggregation.SimpleAggregationObject(cb, conf)

    # Q1     Q2     Q3
    # T: 13  T: 10  T: 8
    # 1:  1  1:  6  1: 2
    # 2:  4  2:  5  2: 3
    # 3:  5  3:  6  3: 3
    # 4:  3
    frame = pandas.DataFrame(columns=["Q1", "Q2", "3"], data=[
        [1, "1,3", 3],
        [2, "1,2", 2],
        [3, "1,2,3", 1],
        [4, 1, 3],
        [2, 2, 2],
        [2, None, 1],
        [3, 1, 3],
        [4, 2, 2],
        [3, "1,3", 1],
        [2, "1,2,3", 3],
        [3, "2,3", 2],
        [4, 3, 1],
        [3, 3, 3],
    ])
    obj.simple_aggregation(frame)
    # check mock
    assert cb.initialize.called
    assert cb.initialize.call_count == 1
    assert cb.update.called
    assert cb.update.call_count == 3
    assert cb.finish.called
    assert cb.finish.call_count == 1

    # check series
    assert len(cb.series) == 3
    assert cb.series[0][0] == "Q1"
    assert cb.series[1][0] == "Q2"
    assert cb.series[2][0] == "3"
    assert isinstance(cb.series[0][1], pandas.Series)
    assert isinstance(cb.series[1][1], pandas.Series)
    assert isinstance(cb.series[2][1], pandas.Series)
    assert cb.series[0][1].values.tolist()[:-1] == [13, 1, 4, 5, 3]
    assert cb.series[1][1].values.tolist() == [10, 6, 5, 6, 1]
    assert cb.series[2][1].values.tolist() == [8, 2, 3, 3]
    assert cb.series[0][1].index.tolist() == ["TOTAL", "a", "b", "c", "d", "BLANK"]
    assert cb.series[1][1].index.tolist() == ["TOTAL", "x", "y", "z", "BLANK"]
    assert cb.series[2][1].index.tolist() == ["TOTAL", "1", "2", "3"]


def test_cross_aggregation_object():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    conf.columnOrder.append("Q4")
    conf.columns["Q4"] = config.Column({
        "title": "Q4",
        "type": config.MULTIPLE,
        "choice": list("qrs"),
    })
    obj = aggregation.CrossAggregationObject(cb, conf)

    # Q1     Q2     Q3    Q4
    # T: 13  T: 10  T: 8  T: 10
    # 1:  1  1:  6  1: 2  1:  3
    # 2:  4  2:  5  2: 3  2:  3
    # 3:  5  3:  7  3: 3  3:  4
    # 4:  3
    #
    # s-m
    #    Q2
    # Q1  T  1  2  3
    #  T 10  6  5  7
    #  1  1  1  -  1
    #  2  4  2  3  2
    #  3  5  3  2  4
    #
    # m-s
    #
    #   Q3
    # Q2  T  1  2  3
    #  T  8  2  3  3
    #  1  6  2  1  3
    #  2  5  1  3  1
    #  3  5  2  1  2
    #
    # s-s
    #    Q3
    # Q1  T  1  2  3
    #  T  8  2  3  3
    #  1  1  -  -  1
    #  2  3  -  2  1
    #  3  4  2  1  1
    #
    # m-m
    #   Q4
    # Q2  T  1  2  3
    #  T 10  3  3  4
    #  1  6  2  1  3
    #  2  5  1  3  1
    #  3  7  3  1  3
    frame = pandas.DataFrame(columns=["Q1", "Q2", "3", "Q4"], data=[
        [1, "1,3", 3, 3],
        [2, "1,2", 2, 2],
        [3, "1,2,3", 1, 1],
        [4, 1, 3, 3],
        [2, 2, 2, 2],
        [2, 3, 1, 1],
        [3, 1, 3, 3],
        [4, 2, 2, 2],
        [3, "1,3", 1, 1],
        [2, "1,2,3", 3, 3],
        [3, "2,3", 2, 2],
        [4, 3, 1, 1],
        [3, 3, 3, 3],
    ])

    # simple x multiple
    crossed = obj.crosstab(frame, "Q1", "Q2")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "a", "b", "c", "d", "BLANK"]
    assert crossed.columns.tolist() == ["TOTAL", "x", "y", "z", "BLANK"]

    assert crossed["TOTAL"].values.tolist()[:-2] == [10, 1, 4, 5]
    assert crossed["x"].values.tolist()[:-2] == [6, 1, 2, 3]
    assert crossed["y"].values.tolist()[:-2] == [5, 0, 3, 2]
    assert crossed["z"].values.tolist()[:-2] == [7, 1, 2, 4]
    for column in crossed.columns:
        assert numpy.isnan(crossed[column].values.tolist()[-2])
        assert numpy.isnan(crossed[column].values.tolist()[-1])

    # muliple x simple
    crossed = obj.crosstab(frame, "Q2", "3")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "x", "y", "z", "BLANK"]
    assert crossed.columns.tolist() == ["TOTAL", "1", "2", "3"]

    assert crossed["TOTAL"].values.tolist()[:-1] == [8, 6, 5, 5]
    assert crossed["1"].values.tolist()[:-1] == [2, 2, 1, 2]
    assert crossed["2"].values.tolist()[:-1] == [3, 1, 3, 1]
    assert crossed["3"].values.tolist()[:-1] == [3, 3, 1, 2]
    for column in crossed.columns:
        assert numpy.isnan(crossed[column].values.tolist()[-1])

    # simple x simple
    crossed = obj.crosstab(frame, "Q1", "3")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "a", "b", "c", "d", "BLANK"]
    assert crossed.columns.tolist() == ["TOTAL", "1", "2", "3"]

    assert crossed["TOTAL"].values.tolist()[:-2] == [8, 1, 3, 4]
    assert crossed["1"].values.tolist()[:-2] == [2, 0, 0, 2]
    assert crossed["2"].values.tolist()[:-2] == [3, 0, 2, 1]
    assert crossed["3"].values.tolist()[:-2] == [3, 1, 1, 1]
    for column in crossed.columns:
        assert numpy.isnan(crossed[column].values.tolist()[-2])
        assert numpy.isnan(crossed[column].values.tolist()[-1])

    # muliple x multiple
    crossed = obj.crosstab(frame, "Q2", "Q4")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "x", "y", "z", "BLANK"]
    assert crossed.columns.tolist() == ["TOTAL", "q", "r", "s", "BLANK"]

    assert crossed["TOTAL"].values.tolist()[:-1] == [10, 6, 5, 7]
    assert crossed["q"].values.tolist()[:-1] == [3, 2, 1, 3]
    assert crossed["r"].values.tolist()[:-1] == [3, 1, 3, 1]
    assert crossed["s"].values.tolist()[:-1] == [4, 3, 1, 3]
    for column in crossed.columns:
        assert numpy.isnan(crossed[column].values.tolist()[-1])

    # test the not existing column
    crossed = obj.crosstab(frame, "not existing1", "not existing2")
    assert crossed.columns.tolist() == ["TOTAL", "BLANK"]
    values = crossed["TOTAL"].values.tolist()
    assert len(values) == 2
    assert numpy.isnan(values[0])
    assert numpy.isnan(values[1])

def test_cross_aggregation_object_with_callback():
    class TestCallback(aggregation.CrossAggregationObject):

        initialize = mock.MagicMock(name="initialize")
        update = mock.MagicMock(name="update")
        finish = mock.MagicMock(name="finish")

        def __init__(self):
            self.frames = {}

        def addDataFrame(self, key, target, crossed):
            if target not in self.frames:
                self.frames[target] = {}
            self.frames[target][key] = frame
    cb = TestCallback()
    conf = config.Config(CONFIG)
    obj = aggregation.CrossAggregationObject(cb, conf)

    # Q1     Q2     Q3
    # T: 13  T: 10  T: 8
    # 1:  1  1:  6  1: 2
    # 2:  4  2:  5  2: 3
    # 3:  5  3:  7  3: 3
    # 4:  3
    frame = pandas.DataFrame(columns=["Q1", "Q2", "3"], data=[
        [1, "1,3", 3],
        [2, "1,2", 2],
        [3, "1,2,3", 1],
        [4, 1, 3],
        [2, 2, 2],
        [2, 3, 1],
        [3, 1, 3],
        [4, 2, 2],
        [3, "1,3", 1],
        [2, "1,2,3", 3],
        [3, "2,3", 2],
        [4, 3, 1],
        [3, 3, 3],
    ])
    obj.cross_aggregation(frame)
    # check mock
    assert cb.initialize.called
    assert cb.initialize.call_count == 1
    assert cb.update.called
    assert cb.update.call_count == 2
    assert cb.finish.called
    assert cb.finish.call_count == 1

    # check series
    assert len(cb.frames) == 1
    assert len(cb.frames["Q1"]) == 2


def test_cross_aggregation_object_with_dropna():
    cb = mock.Mock()
    conf = config.Config(CONFIG)
    conf.columnOrder.append("Q4")
    conf.columns["Q4"] = config.Column({
        "title": "Q4",
        "type": config.MULTIPLE,
        "choice": list("qrs"),
    })
    obj = aggregation.CrossAggregationObject(cb, conf, dropna=True)

    frame = pandas.DataFrame(columns=["Q1", "Q2", "3", "Q4"], data=[
        [1, "1,3", 3, 3],
        [2, None, 2, 2],
        [3, "1,2,3", 1, None],
        [None, 1, 3, 3],
        [2, 2, 2, 2],
        [2, None, 1, 1],
        [None, 1, 3, 3],
        [4, 2, 2, None],
        [3, "1,3", 1, 1],
        [None, None, 3, 3],
        [3, "2,3", 2, 2],
        [4, 3, 1, 1],
        [3, 3, 3, None],
    ])

    # simple x multiple
    crossed = obj.crosstab(frame, "Q1", "Q2")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "a", "b", "c", "d"]
    assert crossed.columns.tolist() == ["TOTAL", "x", "y", "z"]

    # check nan
    numpy.isnan(crossed["x"]["b"])
    numpy.isnan(crossed["y"]["a"])
    numpy.isnan(crossed["z"]["b"])
    assert crossed["TOTAL"].values.tolist()[:-1] == [6, 1, 1, 4]
    assert crossed["x"].values.tolist()[:-1] == [3, 1, 0, 2]
    assert crossed["y"].values.tolist()[:-1] == [3, 0, 1, 2]
    assert crossed["z"].values.tolist()[:-1] == [5, 1, 0, 4]
    # check nan
    for column in crossed.columns:
        # d is ignored value
        assert numpy.isnan(crossed[column].values.tolist()[-1])

    # muliple x simple
    crossed = obj.crosstab(frame, "Q2", "3")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "x", "y", "z"]
    assert crossed.columns.tolist() == ["TOTAL", "1", "2", "3"]

    assert crossed["TOTAL"].values.tolist() == [7, 5, 3, 4]
    assert crossed["1"].values.tolist() == [2, 2, 1, 2]
    assert crossed["2"].values.tolist() == [2, 0, 2, 1]
    assert crossed["3"].values.tolist() == [3, 3, 0, 1]

    # simple x simple
    crossed = obj.crosstab(frame, "Q1", "3")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "a", "b", "c", "d"]
    assert crossed.columns.tolist() == ["TOTAL", "1", "2", "3"]

    assert crossed["TOTAL"].values.tolist()[:-1] == [5, 1, 1, 3]
    assert crossed["1"].values.tolist()[:-1] == [2, 0, 0, 2]
    assert crossed["2"].values.tolist()[:-1] == [2, 0, 1, 1]
    assert crossed["3"].values.tolist()[:-1] == [1, 1, 0, 0]
    # check nan
    for column in crossed.columns:
        assert numpy.isnan(crossed[column].values.tolist()[-1])

    # muliple x multiple
    crossed = obj.crosstab(frame, "Q2", "Q4")
    assert isinstance(crossed, pandas.DataFrame)

    assert crossed.index.tolist() == ["TOTAL", "x", "y", "z"]
    assert crossed.columns.tolist() == ["TOTAL", "q", "r", "s"]

    assert crossed["TOTAL"].values.tolist() == [6, 4, 2, 3]
    assert crossed["q"].values.tolist() == [1, 1, 0, 1]
    assert crossed["r"].values.tolist() == [2, 0, 2, 1]
    assert crossed["s"].values.tolist() == [3, 3, 0, 1]

    # test the not existing column
    crossed = obj.crosstab(frame, "not existing1", "not existing2")
    assert crossed.columns.tolist() == ["TOTAL"]
    values = crossed["TOTAL"].values.tolist()
    assert len(values) == 1
    assert numpy.isnan(values[0])
