# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot

import pandas

import aggregation
import config
import progress


class QAggregationObject(progress.ProgressObject):
    def __init__(self, parent=None):
        """
        :type parent: QObject
        """
        super(QAggregationObject, self).__init__(parent)

    def initialize(self, maximum):
        """
        :type maximum: int
        :param maximum: maximum of progress
        """
        self.initialized.emit(maximum)

    def update(self, current):
        """
        :type current: int
        :param current: current value of progress
        """
        self.updated.emit(current)

    def finish(self):
        self.finished.emit()

    @pyqtSlot(config.Config, pandas.DataFrame, bool)
    def aggregate(self, conf, frame, dropna):
        raise NotImplementedError

class SimpleAggregationObject(QAggregationObject, aggregation.SimpleAggregationCallback):
    @pyqtSlot(config.Config, pandas.DataFrame, bool, dict, dict)
    def aggregate(self, conf, frame, dropna, strings={}, options={}):
        """
        :type conf: config.Config
        :type frame: pandas.DataFrame
        :type dropna: bool
        :type strings: dict[str, str]
        :type options: dict[str, object]
          - :type extend_refs: bool
          - :type aggregate_error: bool
        """
        impl = aggregation.SimpleAggregationObject(self, conf, dropna=dropna, strings=strings, **options)
        impl.simple_aggregation(frame)

class CrossAggregationObject(QAggregationObject, aggregation.CrossAggregationCallback):
    @pyqtSlot(config.Config, pandas.DataFrame, bool, dict, dict)
    def aggregate(self, conf, frame, dropna, strings={}, options={}):
        """
        :type conf: config.Config
        :type frame: pandas.DataFrame
        :type dropna: bool
        :type strings: dict[str, str]
        :type options: dict[str, object]
          - :type extend_refs: bool
          - :type aggregate_error: bool
        """
        impl = aggregation.CrossAggregationObject(self, conf, dropna=dropna, strings=strings, **options)
        impl.cross_aggregation(frame)
