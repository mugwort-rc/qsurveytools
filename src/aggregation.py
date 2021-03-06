# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

import pandas

from . import callback
from . import config
from . import utils

class AggregationCallback(callback.Callback):
    def addSeries(self, column, series):
        raise NotImplementedError

    def addDataFrame(self, index, column, frame):
        raise NotImplementedError

class SimpleAggregationCallback(AggregationCallback):
    def addDataFrame(self, *args, **kwargs):
        print("Warning: SimpleAggregationCallback does not implement addDataFrame()", file=sys.stderr)

class CrossAggregationCallback(AggregationCallback):
    def addSeries(self, *args, **kwargs):
        print("Warning: CrossAggregationCallback does not implement addSeries()", file=sys.stderr)


class AggregationObject(object):
    def __init__(self, cb, conf, dropna=False, strings={}, extend_refs=False, aggregate_error=False):
        self.TOTAL_STR = strings.get("TOTAL", "TOTAL")
        self.BLANK_STR = strings.get("BLANK", "BLANK")
        self.ERROR_STR = strings.get("ERROR", "ERROR")

        self.cb = cb

        self.config = conf
        self.dropna = dropna
        self.filter = config.FilterController(conf)
        self.extend_refs = extend_refs
        self.aggregate_error = aggregate_error

    def filteredFrame(self, frame, columns, extend_refs=False):
        """
        :type frame: pandas.DataFrame
        :param frame: source data frame
        :type columns: list[str]
        :param columns: filter key columns
        :type extend_refs: bool
        :param extend_refs: extend to referenced config
        :rtype: pandas.DataFrame
        :return: filtered data frame
        """
        for column in columns:
            # nan skip
            if isinstance(column, float) and pandas.np.isnan(column):
                continue
            frame = self.filter.applyFilter(frame, column, extend_refs=extend_refs)
        return frame

    def reindex(self, data, column, axis, prefix=[], suffix=[], errors=[], named_index=True):
        # create index set
        items = []
        index_set = set()
        if column in self.config.columns:
            items = self.config.columns[column].choice
            index_set = set(list(range(1, len(items)+1)))
        # detect error index
        index = getattr(data, axis)
        error_index = []
        error_ignore = prefix + suffix + errors
        for idx in index:
            if idx not in index_set and idx not in error_ignore:
                error_index.append(idx)
        data = data.copy()
        kwargs = {
            axis: prefix+list(range(1, len(items)+1))+error_index+suffix+errors,
        }
        data = data.reindex(**kwargs)
        if named_index:
            setattr(data, axis, prefix+items+error_index+suffix+errors)
        return data

class SimpleAggregationObject(AggregationObject):
    def simple_aggregation(self, frame):
        """
        :type frame: pandas.DataFrame
        :param frame: source data frame
        """
        self.cb.initialize(len(self.config.columnOrder))
        for i, column in enumerate(self.config.columnOrder, 1):
            self.cb.update(i)
            vc = self.value_counts(frame, column)
            self.cb.addSeries(column, vc)
        self.cb.finish()

    def value_counts(self, frame, column, named_index=True):
        """
        :type frame: pandas.DataFrame
        :param frame: source data frame
        :type column: str
        :param column: target column
        :type named_index: bool
        :param named_index: reindex to named index
        :type extend_refs: bool
        :param extend_refs: extend to referenced config
        :rtype: pandas.Series
        :return: result of single aggregation
        """
        # check config error
        if column not in self.config.columns:
            return self.reindex(pandas.Series(), column, named_index, self.dropna)
        # check source error
        if column not in frame.columns:
            return self.reindex(pandas.Series(), column, named_index, self.dropna)
        # get column config
        conf = self.config.columns.get(column, config.Column())
        # check column type
        if conf.type not in [config.SINGLE, config.MULTIPLE]:
            return self.reindex(pandas.Series(), column, named_index, self.dropna)
        # get dropna
        dropna = self.dropna or conf.complete
        # apply filter
        frame = self.filteredFrame(frame, [column], extend_refs=self.extend_refs)
        # aggregation
        if conf.type == config.SINGLE:
            return self.single_value_counts(frame, column, named_index, dropna)
        elif conf.type == config.MULTIPLE:
            return self.multiple_value_counts(frame, column, named_index, dropna)
        # error case
        return self.reindex(pandas.Series(), column, named_index, dropna)

    def single_value_counts(self, frame, column, named_index, dropna):
        """
        :type frame: pandas.DataFrame
        :param frame: source data frame
        :type column: str
        :param column: target column
        :type named_index: bool
        :param named_index: reindex to named index
        :type dropna: bool
        :param dropna: drop N/A
        """
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        series = frame[column]
        if dropna:
            series = series.dropna()
        else:
            series = series.fillna(BLANK)
        vc = pandas.value_counts(series, sort=False)
        vc.at[TOTAL] = len(series)
        return self.reindex(vc, column, named_index, dropna)

    def multiple_value_counts(self, frame, column, named_index, dropna):
        """
        :type frame: pandas.DataFrame
        :param frame: source data frame
        :type column: str
        :param column: target column
        :type named_index: bool
        :param named_index: reindex to named index
        :type dropna: bool
        :param dropna: drop N/A
        """
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        series = frame[column]
        if dropna:
            series = series.dropna()
        frame = utils.expand_multiple(series)
        vc_frame = pandas.melt(frame).dropna().groupby("value").agg(len)
        vc = vc_frame["variable"] if "variable" in vc_frame else pandas.Series()
        vc.at[TOTAL] = len(frame.index)
        blank = len(series)-series.count()  # total - notnull
        if not dropna and blank > 0:
            vc.at[BLANK] = blank
        return self.reindex(vc, column, named_index, dropna)

    def reindex(self, series, column, named_index, dropna):
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        ERROR = self.ERROR_STR
        suffix = [BLANK] if not dropna else []
        errors = [ERROR] if self.aggregate_error else []
        return super(SimpleAggregationObject, self).reindex(series, column, "index", prefix=[TOTAL], suffix=suffix, errors=errors, named_index=named_index)


class CrossAggregationObject(AggregationObject):
    def cross_aggregation(self, frame, values=None, aggfunc=None):
        self.cb.initialize(len(self.config.cross.keys)*len(self.config.cross.targets))
        for i, key in enumerate(self.config.cross.keys):
            base = i * len(self.config.cross.targets)
            for j, target in enumerate(self.config.cross.targets, 1):
                self.cb.update(base + j)
                crossed = self.crosstab(frame, key.id, target.id, values=values, aggfunc=aggfunc)
                self.cb.addDataFrame(key.id, target.id, crossed)
        self.cb.finish()

    def crosstab(self, frame, index, column, values=None, aggfunc=None):
        """
        :type frame: pandas.DataFrame
        :param frame: source frame
        :type index: str
        :param index: column name of index side
        :type column: str
        :param column: column name of column side
        :type values: str
        :param values: column name for aggfunc values
        :type aggfunc: callable
        :param aggfunc: aggregation function
        :type extend_refs: bool
        :param extend_refs: extend to referenced config
        :rtype: pandas.DataFrame
        :return: result of cross aggregation
        """
        # check config
        if index not in self.config.columns or column not in self.config.columns:
            return self.reindex(pandas.DataFrame(), index, column, self.dropna, self.dropna)
        # check source
        if index not in frame.columns or column not in frame.columns:
            return self.reindex(pandas.DataFrame(), index, column, self.dropna, self.dropna)
        # get configs
        index_conf = self.config.columns.get(index, config.Column())
        column_conf = self.config.columns.get(column, config.Column())
        # get complete
        index_dropna = self.dropna or index_conf.complete
        column_dropna = self.dropna or column_conf.complete
        # check same
        if index == column:
            return self.reindex(pandas.DataFrame(), index, column, index_dropna, column_dropna)
        # check type
        if index_conf.type not in [config.SINGLE, config.MULTIPLE]:
            return self.reindex(pandas.DataFrame(), index, column, index_dropna, column_dropna)
        if column_conf.type not in [config.SINGLE, config.MULTIPLE]:
            return self.reindex(pandas.DataFrame(), index, column, index_dropna, column_dropna)
        # apply filter
        frame = self.filteredFrame(frame, [index, column], extend_refs=self.extend_refs)
        if len(frame) == 0:
            # empty
            return self.reindex(pandas.DataFrame(), index, column, index_dropna, column_dropna)
        # make arguments
        args = (frame, index, column, index_dropna, column_dropna)
        kwargs = dict(values=values, aggfunc=aggfunc)
        # aggregations
        if index_conf.type == config.SINGLE:
            if column_conf.type == config.SINGLE:
                return self.ss_crosstab(*args, **kwargs)
            elif column_conf.type == config.MULTIPLE:
                return self.sm_crosstab(*args, **kwargs)
        elif index_conf.type == config.MULTIPLE:
            if column_conf.type == config.SINGLE:
                return self.ms_crosstab(*args, **kwargs)
            elif column_conf.type == config.MULTIPLE:
                return self.mm_crosstab(*args, **kwargs)

    def ss_crosstab(self, frame, index, column, index_dropna, column_dropna, values=None, aggfunc=len):
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        drop_targets = []
        if index_dropna:
            drop_targets.append(index)
        if column_dropna:
            drop_targets.append(column)
        if drop_targets:
            dropped_index = frame[drop_targets].dropna().index
            frame = frame.ix[dropped_index]
        if index_dropna:
            iseries = frame[index]
        else:
            iseries = frame[index].fillna(BLANK)
        if column_dropna:
            cseries = frame[column]
        else:
            cseries = frame[column].fillna(BLANK)
        kwargs = {
            'aggfunc': aggfunc,
        }
        if values is not None:
            kwargs['values'] = frame[values]
        crossed = pandas.crosstab(iseries, cseries, margins=True, **kwargs)
        return self.reindex(crossed, index, column, index_dropna, column_dropna)

    def sm_crosstab(self, frame, index, column, index_dropna, column_dropna, values=None, aggfunc=len):
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        drop_targets = []
        if index_dropna:
            drop_targets.append(index)
        if column_dropna:
            drop_targets.append(column)
        if drop_targets:
            dropped_index = frame[drop_targets].dropna().index
            frame = frame.ix[dropped_index]
        if index_dropna:
            iseries = frame[index]
        else:
            iseries = frame[index].fillna(BLANK)
        if column_dropna:
            cframe = utils.expand_multiple(frame[column])
        else:
            cframe = utils.expand_multiple(frame[column].fillna(BLANK))
        iframe = pandas.DataFrame()
        iframe["key"] = iseries
        iframe["index"] = iseries.index
        columns = list(map(lambda x: "col_{}".format(x), cframe.columns))
        cframe.columns = columns
        cframe["index"] = cframe.index
        cframe[None] = self.gen_blanks(frame, column)
        aframe = pandas.melt(cframe.merge(iframe, on="index"), id_vars=["key"], value_vars=columns)
        kwargs = {
            'aggfunc': aggfunc,
        }
        if values is not None:
            vframe = self.gen_values(frame, values)
            vseries = pandas.merge(aframe, vframe, on="index")["values"]
            kwargs['values'] = vseries
        crossed = pandas.crosstab(aframe["key"], aframe["value"], **kwargs)
        crossed = self.update_all(crossed, frame, index, column)
        return self.reindex(crossed, index, column, index_dropna, column_dropna)

    def ms_crosstab(self, frame, index, column, index_dropna, column_dropna, values=None, aggfunc=len):
        return self.sm_crosstab(frame, column, index, column_dropna, index_dropna, values=values, aggfunc=aggfunc).T

    def mm_crosstab(self, frame, index, column, index_dropna, column_dropna, values=None, aggfunc=len):
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        drop_targets = []
        if index_dropna:
            drop_targets.append(index)
        if column_dropna:
            drop_targets.append(column)
        if drop_targets:
            dropped_index = frame[drop_targets].dropna().index
            frame = frame.ix[dropped_index]
            iframe = utils.expand_multiple(frame[index])
            cframe = utils.expand_multiple(frame[column])
        else:
            iframe = utils.expand_multiple(frame[index])
            cframe = utils.expand_multiple(frame[column])
        icolumns = ['row_{}'.format(x) for x in iframe.columns]
        ccolumns = ['col_{}'.format(x) for x in cframe.columns]
        iframe.columns = icolumns
        cframe.columns = ccolumns
        if not index_dropna:
            iframe["blank"] = self.gen_blanks(frame, index)
        if not column_dropna:
            cframe["blank"] = self.gen_blanks(frame, column)
        iframe["index"] = iframe.index
        cframe["index"] = cframe.index
        aframe = pandas.merge(pandas.melt(iframe, id_vars=["index"]),
                              pandas.melt(cframe, id_vars=["index"]),
                              on="index")
        kwargs = {
            'aggfunc': aggfunc,
        }
        if values is not None:
            vframe = self.gen_values(frame, values)
            vseries = pandas.merge(aframe, vframe, on="index")["values"]
            kwargs['values'] = vseries
        crossed = pandas.crosstab(aframe["value_x"], aframe["value_y"], **kwargs)
        crossed = self.update_all(crossed, frame, index, column)
        return self.reindex(crossed, index, column, index_dropna, column_dropna)

    def reindex(self, frame, index, column, index_dropna, column_dropna):
        TOTAL = self.TOTAL_STR
        BLANK = self.BLANK_STR
        ERROR = self.ERROR_STR
        index_suffix = [BLANK] if not index_dropna else []
        column_suffix = [BLANK] if not column_dropna else []
        errors = [ERROR] if self.aggregate_error else []
        frame = super(CrossAggregationObject, self).reindex(frame, index, 'index', prefix=['All'], suffix=index_suffix, errors=errors)
        frame = super(CrossAggregationObject, self).reindex(frame, column, 'columns', prefix=['All'], suffix=column_suffix, errors=errors)
        frame.index = [TOTAL] + frame.index.tolist()[1:]
        frame.columns = [TOTAL] + frame.columns.tolist()[1:]
        return frame

    def gen_blanks(self, frame, column):
        BLANK = self.BLANK_STR
        result = pandas.Series(index=frame.index)
        result[frame[column].isnull()] = BLANK
        return result

    def gen_values(self, frame, values):
        result = frame[[values]].copy()
        result.columns = ["values"]
        result["index"] = frame.index
        return result

    def update_all(self, crossed, frame, index, column):
        result = crossed.copy()
        # insert All row & col
        sub = self.simple_aggregation_object()
        ivc = sub.value_counts(frame, index, named_index=False)
        cvc = sub.value_counts(frame, column, named_index=False)
        result.loc["All"] = cvc[result.columns]
        ivc.index = ["All"] + ivc.index.tolist()[1:]
        result["All"] = ivc[result.index]
        return result

    def simple_aggregation_object(self):
        strings = {
            "BLANK": self.BLANK_STR,
            "TOTAL": self.TOTAL_STR,
        }
        return SimpleAggregationObject(self.cb, self.config, self.dropna, strings)
