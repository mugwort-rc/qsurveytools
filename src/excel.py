# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import math
import numpy
import pandas
import six
import xlsxwriter
from xlsxwriter import utility

EXCEL_CELL_WIDTH = 72.0
EXCEL_CELL_HEIGHT = 18.0

class ExcelSheet(object):
    def __init__(self, sheet, book):
        self.book = book
        self.sheet = sheet

        self.current_row = 1
        self.current_col = 1

        self.table_format = self.book.add_format()
        self.table_format.set_border()

    def setTitle(self, text):
        self.write(0, 0, text)
        self.current_row += 1

    def addPadding(self, size):
        self.current_row += size

    def paste(self, frame_or_series):
        if isinstance(frame_or_series, pandas.Series):
            self.pasteSeries(frame_or_series)
        elif isinstance(frame_or_series, pandas.DataFrame):
            self.pasteDataFrame(frame_or_series)

    def pasteSeries(self, series):
        for i, value in enumerate(series):
            self.write(i, 0, series.index[i], self.table_format)
            self.write(i, 1, value, self.table_format)
        self.current_row += len(series)

    def pasteDataFrame(self, frame):
        self.write(0, 0, '', self.table_format)
        for x, column in enumerate(frame):
            self.write(0, x+1, column, self.table_format)
            for y, value in enumerate(frame[column]):
                if x == 0:
                    self.write(y+1, 0, frame.index[y], self.table_format)
                self.write(y+1, x+1, value, self.table_format)
        self.current_row += len(frame)

    def write(self, row, column, value, *args):
        # TODO: increment, prefix etc...
        if isinstance(value, float) and numpy.isnan(value):
            value = None
        self.sheet.write(self.current_row+row, self.current_col+column, value, *args)

    def merge_write(self, row, column, height, width, value, *args):
        if isinstance(value, float) and numpy.isnan(value):
            value = None
        rng = "{}:{}".format(
            utility.xl_rowcol_to_cell(self.current_row+row, self.current_col+column),
            utility.xl_rowcol_to_cell(self.current_row+row+height, self.current_col+column+width))
        self.sheet.merge_range(rng, value, *args)

    @property
    def name(self):
        return self.sheet.get_name()


class ExcelBook(object):

    SHEET = ExcelSheet

    def __init__(self, filepath, **kwargs):
        self.book = xlsxwriter.Workbook(filepath)
        self.options = kwargs

    def close(self):
        self.book.close()

    def worksheet(self, name=None):
        return self.SHEET(self.book.add_worksheet(name), self.book, **self.options)


SURVEY_FORMULA = '=IFERROR({}/{}%, "")'

class SurveyExcelSheet(ExcelSheet):
    def __init__(self, sheet, book, **kwargs):
        super(SurveyExcelSheet, self).__init__(sheet, book)
        with_percent = kwargs.get("with_percent", False)

        self.percent_format = self.book.add_format({
            'num_format': '0.0' + ('"%"' if with_percent else "")
        })
        self.percent_format.set_border()
        self.chart_row = None

    def paste(self, frame_or_series, **kwargs):
        if isinstance(frame_or_series, pandas.Series):
            self.pasteSeries(frame_or_series, **kwargs)
        elif isinstance(frame_or_series, pandas.DataFrame):
            self.pasteDataFrame(frame_or_series, **kwargs)

    def pasteSeries(self, series, **kwargs):
        """
        :type series: pandas.Series
        :param series: series
        :type with_formula: bool
        :param with_formula: insert rate column
        :type with_chart: bool
        :param with_chart: insert rate chart
        :type to_pie: bool
        :param to_pie: change to pie chart
        :type builder: ChartBuilder
        :param builder: chart builder
        """
        with_formula = kwargs.get('with_formula', True)
        to_pie = kwargs.get("to_pie", False)
        start = None
        for i, value in enumerate(series):
            if i == 0:
                start = self.cell(i, 1, row_abs=True)
            self.write(i, 0, series.index[i], self.table_format)
            self.write(i, 1, value, self.table_format)
            if with_formula:
                self.write(i, 2, SURVEY_FORMULA.format(self.cell(i, 1), start), self.percent_format)

        with_chart = kwargs.get("with_chart", True)
        Builder = kwargs.get("builder", SimpleBarChartBuilder)
        if with_chart and issubclass(Builder, ChartBuilder):
            builder = Builder(series)
            chart = builder.makeChart(self, self.current_row, self.current_col, to_pie=to_pie)
            self.sheet.insert_chart(
                # back to title row
                self.current_row,
                # 2[index, N] + (1[F]) + X[defined by builder]
                self.current_col+2+(1 if with_formula else 0)+max(1, Builder.TABLE_MARGIN),
                chart)
            self.chart_row = None  # reset chart_row

        self.current_row += len(series)

    def pasteDataFrame(self, frame, **kwargs):
        with_formula = kwargs.get('with_formula', True)
        table_start = 0
        left_header = 1
        formula_start = len(frame.columns) + left_header*2
        self.write(0, table_start, "", self.table_format)
        if with_formula:
            self.write(0, formula_start, "%", self.table_format)
        # generate left-most total cells
        starts = [self.cell(i+1, table_start+1, row_abs=True) for i in range(len(frame.index))]
        for x, column in enumerate(frame):
            # write table column
            self.write(0, table_start+x+1, column, self.table_format)
            # write table column for formula (skip TOTAL)
            if with_formula and x != 0:
                # write to
                #      row: 0 (header row)
                #   column: formula_start + x + 1 (column header) - 1 (skip total)
                self.write(0, formula_start+x, column, self.table_format)
            for y, value in enumerate(frame[column]):
                # write column header
                if x == 0:
                    # write table index
                    self.write(y+1, table_start, frame.index[y], self.table_format)
                    # write table index for formula
                    if with_formula:
                        self.write(y+1, formula_start, frame.index[y], self.table_format)
                # write to value table
                self.write(y+1, x+1, value, self.table_format)
                # write to formula table
                if with_formula and x != 0:
                    # write to
                    #    row: y + 1 (row header)
                    # column: formula_start + x + 1 (column header) - 1 (skip total)
                    self.write(y+1, formula_start+x, SURVEY_FORMULA.format(self.cell(y+1, x+1), starts[y]), self.percent_format)

        self.add_cross_chart(frame, formula_start, **kwargs)

        self.current_row += len(frame)

    def cell(self, row, col, row_abs=False, col_abs=False):
        return utility.xl_rowcol_to_cell(
            self.current_row+row,
            self.current_col+col,
            row_abs,
            col_abs
        )

    def add_cross_chart(self, frame, formula_start, **kwargs):
        with_chart = kwargs.get("with_chart", True)
        Builder = kwargs.get("builder", CrossStackedChartBuilder)
        if with_chart and issubclass(Builder, ChartBuilder):
            chart_frame = frame.copy()
            # TODO: drop the user-specified index value
            builder = Builder(chart_frame)
            chart = builder.makeChart(self, self.current_row, formula_start+1)
            if self.chart_row is None:
                self.chart_row = self.current_row
            self.sheet.insert_chart(
                # back to title row
                self.chart_row,
                # column
                (
                    # (formula_start+1(to real start point))
                    (formula_start+1) +
                    # (1(header)+columns-1('All'))
                    (len(frame.columns)) +
                    # padding[defined by builder]
                    max(1, Builder.TABLE_MARGIN)
                    ),
                # chart object
                chart)
            # increment chart_row
            self.chart_row += int(math.ceil(builder.chartHeight() / EXCEL_CELL_HEIGHT))


class CrossSingleTableSheet(SurveyExcelSheet):
    def __init__(self, sheet, book, **kwargs):
        super(CrossSingleTableSheet, self).__init__(sheet, book, **kwargs)
        self.common_header = None
        self.last_total = pandas.Series()
        self.fixed_header = None
        self.merge_format = self.book.add_format()
        self.merge_format.set_border()
        self.merge_format.set_align("justify")
        self.merge_format.set_align("top")

    def setCommonHeader(self, frame, **kwargs):
        if self.common_header is not None:
            raise Exception("Common header is already set.")
        self.common_header = frame.columns.tolist()
        self.fixed_header = self.current_row
        with_formula = kwargs.get('with_formula', True)
        table_start = 1
        left_header = 2
        formula_start = len(frame.columns) + left_header*2
        self.merge_write(0, table_start-1, 0, 1, "", self.merge_format)
        if with_formula:
            self.merge_write(0, formula_start-1, 0, 1, "%", self.merge_format)
        for x, column in enumerate(frame):
            # write table column
            self.write(0, table_start+x+1, column, self.table_format)
            # write table column for formula (skip TOTAL)
            if with_formula and x != 0:
                # write to
                #      row: 0 (header row)
                #   column: formula_start + x + 1 (column header) - 1 (skip total)
                self.write(0, formula_start+x, column, self.table_format)

    def pasteDataFrame(self, frame, **kwargs):
        #assert frame.index[0] == "All"
        if self.common_header is None:
            self.setCommonHeader(frame, **kwargs)
        else:
            if self.common_header != frame.columns.tolist():
                raise Exception("columns does not match the common header.")

        with_formula = kwargs.get('with_formula', True)
        # check first series (except total series.)
        current_total = frame.iloc[0].copy().fillna(0)
        skip_total = self.last_total.tolist() == current_total.tolist()
        if not skip_total:
            self.last_total = current_total
        table_start = 1
        left_header = 2
        formula_start = len(frame.columns) + left_header*2
        # write table categories
        self.merge_write(
            # row
            1 if skip_total else 2,
            # col
            table_start-1,  # TODO: remove this relative `-1`
            # height, width
            len(frame.index)-2, 0,
            # value
            kwargs.get("name", ""),
            self.merge_format)
        if with_formula:
            self.merge_write(
                # row
                1 if skip_total else 2,
                # col
                formula_start-1,  # TODO: remove this relative `-1`
                # height, width
                len(frame.index)-2, 0,
                # value
                kwargs.get("name", ""),
                self.merge_format)
        # generate left-most total cells
        starts = [self.cell(i+(0 if skip_total else 1), table_start+1, row_abs=True) for i in range(len(frame.index))]
        for x, column in enumerate(frame):
            #    [0]      | [1]
            # 0:          | common headers
            #    ---------|--------------
            # 1: [total]  | data...
            # 2: [index1] | data...
            index_start = 1  # common header skip
            for y, value in enumerate(frame[column]):
                # check skip_total
                if skip_total and y == 0:
                    assert index_start == 1
                    index_start -= 1  # skip back; total row
                    continue
                # write index header
                if x == 0:
                    #       |            | common headers...
                    # ------|------------|--------
                    # [a] TOTAL          | ...
                    # TABLE | [b] INDEX1 |
                    #       | [b] INDEX2 |
                    # ...
                    # [a]: for TOTAL
                    if y == 0:
                        # write table index
                        self.merge_write(
                            # row, col
                            y+index_start, table_start-1,
                            0, 1,
                            # value
                            frame.index[y],
                            # cell format
                            self.merge_format)
                        # write table index for formula
                        if with_formula:
                            self.merge_write(
                                # row, col
                                y+index_start, formula_start-1,
                                0, 1,
                                # value
                                frame.index[y],
                                # cell format
                                self.merge_format)
                    # [b]: for other
                    else:
                        # write table index
                        self.write(
                            # row, col
                            y+index_start, table_start,
                            # value
                            frame.index[y],
                            # cell format
                            self.table_format)
                        # write table index for formula
                        if with_formula:
                            self.write(
                                # row, col
                                y+index_start, formula_start,
                                # value
                                frame.index[y],
                                # cell format
                                self.table_format)
                # write to value table
                self.write(
                    # row, col
                    y+index_start, table_start+x+1,
                    # value
                    value,
                    # cell format
                    self.table_format)
                # write to formula table
                if with_formula and x != 0:
                    # write to
                    #    row: y + 1 (row header)
                    # column: formula_start + x + 1 (column header) - 1 (skip total)
                    self.write(
                        # row, col
                        y+index_start, formula_start+x,
                        # value
                        SURVEY_FORMULA.format(self.cell(y+index_start, table_start+x+1), starts[y]),
                        # cell format
                        self.percent_format)

        self.add_cross_chart(frame, formula_start, skip_total=skip_total, **kwargs)

        self.current_row += len(frame)
        if skip_total:
            self.current_row -= 1

    def add_cross_chart(self, frame, formula_start, **kwargs):
        with_chart = kwargs.get("with_chart", True)
        skip_total = kwargs.get("skip_total", False)
        Builder = kwargs.get("builder", CrossStackedChartBuilder)
        if with_chart and issubclass(Builder, ChartBuilder):
            chart_frame = frame.copy()
            # TODO: drop the user-specified index value
            builder = Builder(chart_frame)
            chart = builder.makeChart(self, self.current_row, formula_start+1, fixed_header=self.fixed_header, total_skipped=skip_total)
            if self.chart_row is None:
                self.chart_row = self.current_row
            self.sheet.insert_chart(
                # back to title row
                self.chart_row,
                # column
                (
                    # (formula_start+1(to real start point))
                    (formula_start+1) +
                    # (1(header)+columns-1('All'))
                    (len(frame.columns)) +
                    # padding[defined by builder]
                    max(1, Builder.TABLE_MARGIN)
                    ),
                # chart object
                chart)
            # increment chart_row
            self.chart_row += int(math.ceil(builder.chartHeight() / EXCEL_CELL_HEIGHT))


class CrossAzemichiTableSheet(SurveyExcelSheet):
    def __init__(self, sheet, book, **kwargs):
        super(CrossAzemichiTableSheet, self).__init__(sheet, book, **kwargs)
        self.common_header = None
        self.last_total = pandas.Series()
        self.fixed_header = None
        self.merge_format = self.book.add_format()
        self.merge_format.set_border()
        self.merge_format.set_align("justify")
        self.merge_format.set_align("top")

    def setCommonHeader(self, frame, **kwargs):
        if self.common_header is not None:
            raise Exception("Common header is already set.")
        self.common_header = frame.columns.tolist()
        self.fixed_header = self.current_row
        table_start = 1
        self.merge_write(0, table_start-1, 0, 1, "", self.merge_format)
        for x, column in enumerate(frame):
            # write table column
            self.write(0, table_start+x+1, column, self.table_format)

    def pasteDataFrame(self, frame, **kwargs):
        #assert frame.index[0] == "All"
        if self.common_header is None:
            self.setCommonHeader(frame, **kwargs)
        else:
            if self.common_header != frame.columns.tolist():
                raise Exception("columns does not match the common header.")

        # check first series (except total series.)
        current_total = frame.iloc[0].copy().fillna(0)
        skip_total = self.last_total.tolist() == current_total.tolist()
        if not skip_total:
            self.last_total = current_total
        table_start = 1
        # write table categories
        self.merge_write(
            # row
            1 if skip_total else 3,
            # col
            table_start-1,  # TODO: remove this relative `-1`
            # height, width
            len(frame.index)*2-3, 0,
            # value
            kwargs.get("name", ""),
            self.merge_format)
        # generate left-most total cells
        starts = [self.cell(i*2+(-1 if skip_total else 1), table_start+1, row_abs=True) for i in range(len(frame.index))]
        for x, column in enumerate(frame):
            #    [0]          | [1]
            # 0:              | common headers
            #    -------------|--------------
            # 1: [total]      | data...
            # 2: [data/total] | %
            # 3: [index1]     | data...
            # 4: [data/total] | %
            index_start = 1  # common header skip
            for y, value in enumerate(frame[column]):
                # check skip_total
                if skip_total and y == 0:
                    assert index_start == 1
                    index_start -= 2  # skip back; total row
                    continue
                # write index header
                if x == 0:
                    #       |            | common headers...
                    # ------|------------|--------
                    # [a] TOTAL          | ...
                    # TABLE | [b] INDEX1 | value
                    #       |            | formula%
                    #       | [b] INDEX2 |
                    # ...
                    # [a]: for All
                    if y == 0:
                        # write table index
                        self.merge_write(
                            # row, col
                            y*2+index_start, table_start-1,
                            1, 1,
                            # value
                            frame.index[y],
                            # cell format
                            self.merge_format)
                    # [b]: for other
                    else:
                        # write table index
                        self.merge_write(
                            # row, col
                            y*2+index_start, table_start,
                            1, 0,
                            # value
                            frame.index[y],
                            # cell format
                            self.merge_format)
                # write to value table
                self.write(
                    # row, col
                    y*2+index_start, table_start+x+1,
                    # value
                    value,
                    # cell format
                    self.table_format)
                self.write(
                    # row, col
                    y*2+index_start+1, table_start+x+1,
                    # value
                    SURVEY_FORMULA.format(self.cell(y*2+index_start, table_start+x+1), starts[y]),
                    # cell format
                    self.percent_format)

        self.add_cross_chart(frame, table_start, skip_total=skip_total, **kwargs)

        self.current_row += len(frame)*2
        if skip_total:
            self.current_row -= 1*2

    def add_cross_chart(self, frame, table_start, **kwargs):
        # TODO: here
        with_chart = kwargs.get("with_chart", True)
        skip_total = kwargs.get("skip_total", False)
        Builder = kwargs.get("builder", CrossAzemichiChartBuilder)
        if with_chart and issubclass(Builder, ChartBuilder):
            chart_frame = frame.copy()
            # TODO: drop the user-specified index value
            builder = Builder(chart_frame)
            chart = builder.makeChart(self, self.current_row, table_start+1, fixed_header=self.fixed_header, total_skipped=skip_total)
            if self.chart_row is None:
                self.chart_row = self.current_row
            self.sheet.insert_chart(
                # back to title row
                self.chart_row,
                # column
                (
                    # (table_start+1(to real start point))
                    (table_start+1) +
                    # (1(header)+columns-1('All'))
                    (len(frame.columns)) +
                    # padding[defined by builder]
                    max(1, Builder.TABLE_MARGIN)
                    ),
                # chart object
                chart)
            # increment chart_row
            self.chart_row += int(math.ceil(builder.chartHeight() / EXCEL_CELL_HEIGHT))


class SurveyExcelBook(ExcelBook):
    SHEET = SurveyExcelSheet


class ChartBuilder(object):

    TABLE_MARGIN = 2

    def makeChart(self, sheet, row, column):
        """
        :type sheet: SurveyExcelSheet
        :param sheet: write target
        :type row: int
        :param row: start row
        :type column: int
        :param column: start column
        """
        raise NotImplementedError

    def seriesCount(self):
        """
        :rtype: int
        :return: y axis size
        """
        raise NotImplementedError

    def chartHeight(self):
        """
        :rtype: int
        :return: chart height size (px)
        """
        raise NotImplementedError

class SimpleBarChartBuilder(ChartBuilder):
    """
    (C)   | (N)  | (R)
    ======|======|======
    TOTAL | x    | x / x
    A     | a    | a / x
    B     | b    | b / x
    """

    WIDTH = 500
    HEIGHT_PER_SERIES = 25
    HEIGHT_MERGIN = 36
    FONT_PT = 9

    def __init__(self, series):
        super(SimpleBarChartBuilder, self).__init__()
        self.series = series

    def makeChart(self, sheet, row, column, **kwargs):
        """
        :type sheet: SurveyExcelSheet
        :param sheet: write target
        :type row: int
        :param row: start row
        :type column: int
        :param column: start column
        :type to_pie: bool
        :param to_pie: change to pie chart
        """
        to_pie = kwargs.get("to_pie", False)

        COLUMN_C = column
        COLUMN_R = column + 2
        font = {
            "size": self.FONT_PT,
        }

        if to_pie:
            chart = sheet.book.add_chart({
                "type": "pie",
            })
        else:
            chart = sheet.book.add_chart({
                "type": "bar",
                "subtype": "clustered",
            })

        chart.add_series({
            "categories": [
                sheet.name,
                row+1,  # skip TOTAL
                COLUMN_C,  # target to (C)
                row+self.seriesCount(),
                COLUMN_C,
                ],
            "values": [
                sheet.name,
                row+1,  # skip TOTAL
                COLUMN_R,  # target to (R)
                row+self.seriesCount(),
                COLUMN_R,
            ],
            "data_labels": {
                "value": True,
                "position": "outside_end",
                "num_format": '0.0;-0.0;0.0;@',
                "font": font,
            }
        })
        # chart area size
        if to_pie:
            width = self.WIDTH / 1.5
            height = self.HEIGHT_MERGIN + self.HEIGHT_PER_SERIES * 8
        else:
            width = self.WIDTH
            height = self.HEIGHT_MERGIN + self.HEIGHT_PER_SERIES * self.seriesCount()
        chart.set_size({
            "width": width,
            "height": height,
        })
        # plot area size
        longest_category = ""
        for index in self.series.index:
            index = six.text_type(index)
            longest_category = index if len(index) > len(longest_category) else longest_category
        index_width = min(self.FONT_PT * len(longest_category), self.WIDTH / 2)
        if to_pie:
            index_height = self.HEIGHT_PER_SERIES * 8
        else:
            index_height = self.HEIGHT_PER_SERIES * self.seriesCount()
        index_margin = float(index_width) / width
        plot_margin = self.HEIGHT_MERGIN / 2.0
        x_margin = plot_margin / width
        y_margin = plot_margin / height
        if not to_pie:
            chart.set_plotarea({
                "layout": {
                    "x": x_margin + index_margin,
                    "y": y_margin,
                    "width": 1.0 - x_margin - index_margin,
                    "height": float(index_height) / height,
                }
            })
        # axis
        chart.set_x_axis({
            "num_font": font,
            "name_font": font,
            "num_format": "0\"%\"",
        })
        chart.set_y_axis({
            "reverse": True,
            "num_font": font,
            "name_font": font,
        })
        # legend
        if not to_pie:
            chart.set_legend({
                "none": True,
            })
        # chart area
        chart.set_chartarea({
            "border": {
                "none": True,
            },
        })
        return chart

    def seriesCount(self):
        return len(self.series) - 1


class CrossStackedChartBuilder(ChartBuilder):
    """
    (C)   | (R1) | (R2)
    ======|======|======
    TOTAL | t1   | t2
    A     | a1   | a2
    B     | b1   | b2
    """

    WIDTH = 600
    HEIGHT_PER_SERIES = 40
    HEIGHT_MERGIN = 36
    FONT_PT = 9
    LEGEND_TEXT_PT = 12
    LEGEND_PT = 25

    def __init__(self, frame):
        super(CrossStackedChartBuilder, self).__init__()
        self.frame = frame

    def _createChart(self, sheet):
        return sheet.book.add_chart({
            "type": "bar",
            "subtype": "percent_stacked",
        })

    def makeChart(self, sheet, row, column, **kwargs):
        """
        :type sheet: SurveyExcelSheet
        :param sheet: write target
        :type row: int
        :param row: start row
        :type column: int
        :param column: start column
        
        kwargs:
            :type fixed_header: int
            :param fixed_header: fixed header value (default: row)
            :type total_skipped: bool
            :param total_skipped: total row was skipped (default: False)
        """
        # kwargs
        name_header = kwargs.get("fixed_header", row)
        total_skipped = kwargs.get("total_skipped", False)
        index_start = 1 if not total_skipped else 0

        # constants
        COLUMN_C = column
        COLUMN_R1 = column + 1

        font = {
            "size": self.FONT_PT,
        }
        chart = self._createChart(sheet)
        # column-base
        xaxis_count = self.xaxisCount()
        if total_skipped:
            xaxis_count -= 1
        categories = [
            sheet.name,
            row+1+index_start,  # skip "(%)"
            COLUMN_C,  # target to (C)
            row+1+xaxis_count,  # skip "(%)"
            COLUMN_C,
        ]
        for i in range(self.yaxisCount()):
            COLUMN_RC = COLUMN_R1 + i  # R-current
            chart.add_series({
                "name": [
                    sheet.name,
                    name_header,
                    COLUMN_R1+i
                    ],
                "categories": categories,
                "values": [
                    sheet.name,
                    row+1+index_start,  # skip "(%)"
                    COLUMN_RC,  # target to (RC)
                    row+1+xaxis_count,  # skip "(%)"
                    COLUMN_RC,
                ],
                "data_labels": {
                    "value": True,
                    "num_format": '0.0;-0.0;"";@',
                    "font": font,
                },
                "gap": 100,
            })
        # row-base
        """
        COLUMN_RN = COLUMN_R1 + self.yaxisCount()
        for i in range(self.xaxisCount()):
            chart.add_series({
                "name": [
                    sheet.name,
                    row+2+i,  # skip (%), TOTAL
                    COLUMN_C
                    ],
                "categories": [
                    sheet.name,
                    row,
                    COLUMN_R1,  # target to (R1)
                    row,
                    COLUMN_RN,
                    ],
                "values": [
                    sheet.name,
                    row+2+i,  # skip (%), TOTAL
                    COLUMN_R1,  # target to (R1)
                    row+2+i,
                    COLUMN_RN,
                ],
                "data_labels": {
                    "value": True,
                    "percentage": True,
                    "num_format": "0.0;-#.0;"";@",
                    "font": font,
                }
            })
        """
        # chart area size
        width = self.WIDTH
        height = self.chartHeight()
        chart.set_size({
            "width": width,
            "height": height,
        })
        # plot area size
        longest_category = ""
        for index in self.frame.index:
            index = six.text_type(index)
            longest_category = index if len(index) > len(longest_category) else longest_category
        index_width = min(self.FONT_PT * len(longest_category), self.WIDTH / 2)
        index_height = self.HEIGHT_PER_SERIES * self.xaxisCount()
        index_margin = float(index_width) / width
        plot_margin = self.HEIGHT_MERGIN / 2.0
        x_margin = plot_margin / width
        y_margin = plot_margin / height
        x_width = 1.0 - x_margin - index_margin
        y_height = float(index_height) / height
        chart.set_plotarea({
            "layout": {
                "x": x_margin + index_margin,
                "y": y_margin,
                "width": x_width,
                "height": y_height,
            }
        })
        # axis
        chart.set_x_axis({
            "num_font": font,
            "name_font": font,
        })
        chart.set_y_axis({
            "reverse": True,
            "num_font": font,
            "name_font": font,
        })
        # chart area
        chart.set_chartarea({
            "border": {
                "none": True,
            },
        })
        # legend
        chart.set_legend({
            'font': font,
            'layout': {
                'x': index_margin,
                'y': y_margin*2+y_height,
                'width': 1.0-index_margin,
                'height': 1.0-y_margin*2-y_height,
            },
            'position': 'bottom',
        })
        return chart

    def yaxisCount(self):
        return len(self.frame.columns) - 1

    def xaxisCount(self):
        return len(self.frame.index) - 1

    def chartHeight(self):
        """
        :rtype: int
        :return: chart height size (px)
        """
        return (
            self.HEIGHT_MERGIN +
            self.HEIGHT_PER_SERIES * self.xaxisCount() +
            self.LEGEND_PT * self.yaxisCount()
            )



class CrossAzemichiChartBuilder(ChartBuilder):
    """
    (I)   | (C1) | (C2)
    ======|======|======
    TOTAL | t1   | t2
          | t1/t1| t2/t1
    [A]   | a1   | a2
          | a1/a1| a2/a1
    [B]   | b1   | b2
          | b1/b1| b2/b1
    """

    WIDTH = 600
    HEIGHT_PER_SERIES = 40
    HEIGHT_MERGIN = 36
    FONT_PT = 9
    LEGEND_TEXT_PT = 12
    LEGEND_PT = 25

    def __init__(self, frame):
        super(CrossAzemichiChartBuilder, self).__init__()
        self.frame = frame

    def _createChart(self, sheet):
        return sheet.book.add_chart({
            "type": "bar",
            "subtype": "percent_stacked",
        })

    def makeChart(self, sheet, row, column, **kwargs):
        """
        :type sheet: SurveyExcelSheet
        :param sheet: write target
        :type row: int
        :param row: start row
        :type column: int
        :param column: start column

        kwargs:
            :type fixed_header: int
            :param fixed_header: fixed header value (default: row)
            :type total_skipped: bool
            :param total_skipped: total row was skipped (default: False)
        """
        # kwargs
        name_header = kwargs.get("fixed_header", row)
        total_skipped = kwargs.get("total_skipped", False)
        index_start = 2 if not total_skipped else 0  # index of [A]

        # constants
        COLUMN_I = column
        COLUMN_C1 = column + 1

        font = {
            "size": self.FONT_PT,
        }
        chart = self._createChart(sheet)
        # column-base
        xaxis_count = self.xaxisCount()
        # row + 2 + index_start (skip common-header)
        categories = "=({})".format(",".join(["'{}'!{}".format(sheet.name, utility.xl_rowcol_to_cell(row+1+index_start+i*2, COLUMN_I)) for i in range(xaxis_count)]))
        for i in range(self.yaxisCount()):
            current_col = COLUMN_C1 + i + 1  # skip TOTAL
            chart.add_series({
                "name": [
                    sheet.name,
                    name_header,
                    current_col
                    ],
                "categories": categories,
                "values": "=({})".format(",".join(["'{}'!{}".format(sheet.name, utility.xl_rowcol_to_cell(row+2+index_start+i*2, current_col)) for i in range(xaxis_count)])),
                "data_labels": {
                    "value": True,
                    "num_format": '0.0;-0.0;"";@',
                    "font": font,
                },
                "gap": 100,
            })
        # chart area size
        width = self.WIDTH
        height = self.chartHeight()
        chart.set_size({
            "width": width,
            "height": height,
        })
        # plot area size
        longest_category = ""
        for index in self.frame.index:
            index = six.text_type(index)
            longest_category = index if len(index) > len(longest_category) else longest_category
        index_width = min(self.FONT_PT * len(longest_category), self.WIDTH / 2)
        index_height = self.HEIGHT_PER_SERIES * self.xaxisCount()
        index_margin = float(index_width) / width
        plot_margin = self.HEIGHT_MERGIN / 2.0
        x_margin = plot_margin / width
        y_margin = plot_margin / height
        x_width = 1.0 - x_margin - index_margin
        y_height = float(index_height) / height
        chart.set_plotarea({
            "layout": {
                "x": x_margin + index_margin,
                "y": y_margin,
                "width": x_width,
                "height": y_height,
            }
        })
        # axis
        chart.set_x_axis({
            "num_font": font,
            "name_font": font,
        })
        chart.set_y_axis({
            "reverse": True,
            "num_font": font,
            "name_font": font,
        })
        # chart area
        chart.set_chartarea({
            "border": {
                "none": True,
            },
        })
        # legend
        chart.set_legend({
            'font': font,
            'layout': {
                'x': index_margin,
                'y': y_margin*2+y_height,
                'width': 1.0-index_margin,
                'height': 1.0-y_margin*2-y_height,
            },
            'position': 'bottom',
        })
        return chart

    def yaxisCount(self):
        return len(self.frame.columns) - 1

    def xaxisCount(self):
        return len(self.frame.index) - 1

    def chartHeight(self):
        """
        :rtype: int
        :return: chart height size (px)
        """
        return (
            self.HEIGHT_MERGIN +
            self.HEIGHT_PER_SERIES * self.xaxisCount() +
            self.LEGEND_PT * self.yaxisCount()
            )


class PandaObjectInfo(object):
    def __init__(self, obj):
        self.object = obj

        self.columnSize = None
        self.rowSize = None

        self.initInfo()

    def initInfo(self):
        raise NotImplementedError

class PandaSeriesInfo(PandaObjectInfo):
    def initInfo(self):
        self.columnSize = 2  # index, value
        self.rowSize = len(self.object)

class PandaDataFrameInfo(PandaObjectInfo):
    def initInfo(self):
        # index column + columns
        self.columnSize = 1 + len(self.object.columns)
        # column row + rows
        self.rowSize = 1 + len(self.object.index)