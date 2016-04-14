# -*- coding: utf-8 -*-

import numpy

import callback
import config
import utils


class ValidationCallback(callback.Callback):
    def columnNotFound(self, column):
        raise NotImplementedError

    def settingNotFound(self, column):
        raise NotImplementedError

    def settingIsUnknown(self, column):
        raise NotImplementedError

    def validationError(self, column, row, value, **kwargs):
        raise NotImplementedError

    def multipleExceptionError(self, column, row, value, **kwargs):
        raise NotImplementedError

    def limitationError(self, column, row, value, **kwargs):
        raise NotImplementedError

    def forbiddenError(self, column, row, value, **kwargs):
        raise NotImplementedError

    def incompleteError(self, column, row, value, **kwargs):
        raise NotImplementedError


class ValidationObject(object):
    def __init__(self, cb, conf):
        self.cb = cb
        self.config = conf
        self.filter = config.FilterController(self.config)
        self.errors = []

    def registerError(self, column, index):
        self.errors.append((column, index))

    def validate(self, frame):
        has_id = "ID" in frame.columns
        def get_id(i):
            return frame["ID"][i] if has_id else None
        self.cb.initialize(len(self.config.columns))
        for x, column in enumerate(self.config.columns):
            self.cb.update(x)
            # check frame, column exists
            if column not in frame:
                self.cb.columnNotFound(column)
                continue
            series = frame[column]

            # get type
            conf = self.config.columns[column]
            type = conf.get('type', config.UNKNOWN)
            # check type
            if type == config.FREE:
                # no check
                continue
            elif type not in [config.SINGLE, config.MULTIPLE]:
                self.cb.settingIsUnknown(column)
                continue

            # drop N/A
            series = frame[column].dropna()

            # get choice size
            size = len(conf.choice)
            # check answers
            if type == config.SINGLE:
                for i in series[~series.isin(range(1, size+1))].index:
                    self.registerError(column, i)
                    self.cb.validationError(column, i, series[i], id=get_id(i))
            elif type == config.MULTIPLE:
                mframe = utils.expand_multiple_bool(series)
                # check multi-ex
                for v in conf.multiex:
                    if v not in mframe:
                        continue
                    test = series[mframe[v]].apply(utils.int_cast)
                    for i in test[test != v].index:
                        self.registerError(column, i)
                        self.cb.multipleExceptionError(column, i, test[i], id=get_id(i))
                # check range
                for i in range(1, size+1):
                    if i not in mframe:
                        continue
                    del mframe[i]
                for value in mframe.columns:
                    for i in mframe[mframe[value].eq(True)].index:
                        self.registerError(column, i)
                        self.cb.validationError(column, i, value, id=get_id(i))
            # check multiple limit
            if conf.limit > 0 and type == config.MULTIPLE:
                mseries = utils.expand_base(series).apply(len)
                for i in mseries[mseries > conf.limit].index:
                    self.registerError(column, i)
                    self.cb.limitationError(column, i, series[i], id=get_id(i))

            filtered = self.filter.applyFilter(frame, column, extend_refs=True)

            # check complete
            filtered_series = frame[column][frame.index.isin(filtered.index)].notnull()
            complete = conf.get('complete', False)
            if complete and filtered_series.hasnans():
                for i in filtered_series[filtered_series.isnull()].index:
                    self.registerError(column, i)
                    self.cb.incompleteError(column, i, series[i], id=get_id(i))

            # check filtered notnull
            notnull = frame[column][~frame.index.isin(filtered.index)].notnull()
            for i in notnull[notnull == True].index:
                self.registerError(column, i)
                self.cb.forbiddenError(column, i, series[i], id=get_id(i))

        self.cb.finish()

    def errorToNaN(self, frame):
        frame = frame.copy()
        for column, index in self.errors:
            #frame[column][index] = numpy.nan
            frame.loc[index, column] = numpy.nan
        return frame

    def errorToError(self, frame, error_string):
        frame = frame.copy()
        for column, index in self.errors:
            #frame[column][index] = error_string
            frame.loc[index, column] = error_string
        return frame
