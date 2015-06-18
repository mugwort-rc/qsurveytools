# -*- coding: utf-8 -*-

import pythoncom


def com_range(n):
    return range(1, n+1)


def byUsedRange(used, **kwargs):
    import pandas
    table = [[y for y in x] for x in used]
    return pandas.io.parsers.TextParser(table, **kwargs).read()


def collect_sheets(book, sheet_names):
    result = {}
    names = get_sheet_names(book)
    for sheet_name in sheet_names:
        if sheet_name not in names:
            continue
        try:
            result[sheet_name] = book.Worksheets(sheet_name)
        except (AttributeError, pythoncom.com_error) as e:
            continue
    return result


def get_sheet_names(book):
    return [book.Worksheets(i).Name for i in com_range(book.Worksheets.Count)]
