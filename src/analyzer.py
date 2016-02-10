# -*- coding: utf-8 -*-

class Analyzer(object):
    def __init__(self, reserved_names):
        """
        :type reserved_names: dict of (str, str)
        """
        self.reserved_names = reserved_names

    def abstract(self, series_or_frame):
        raise NotImplementedError


class SimpleAggregationAnalyzer(Analyzer):
    def _abstract_info(self, series):
        series = series.copy().fillna(0)
        TOTAL = self.reserved_names.get("TOTAL", "TOTAL")
        assert series.index[0] == TOTAL

        ret = {}
        total = float(series[TOTAL])
        for i, name in enumerate(series.index):
            if name in self.reserved_names.values():
                continue
            value = series[name]
            rate = round(value / total * 100, 1)
            if rate not in ret:
                ret[rate] = []
            ret[rate].append(name)
        return ret


class CrossAggregationAnalyzer(Analyzer):
    pass
