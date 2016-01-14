# -*- coding: utf-8 -*-

import unicodedata
import re

import six
import pandas

CSV_RE = re.compile(r'\s*,\s*')
INT_RE = re.compile(r'\d+')

def and_concat(conds):
    assert len(conds) > 0
    if len(conds) == 1:
        return conds[0]
    return conds[0] & and_concat(conds[1:])

def or_concat(conds):
    assert len(conds) > 0
    if len(conds) == 1:
        return conds[0]
    return conds[0] | or_concat(conds[1:])


def all_false_case(frame):
    conds = []
    for column in frame.columns:
        conds.append(frame[column].eq(False))
    return and_concat(conds)


def is_nans(array):
    """
    :type array: list of value or pandas.Series
    """
    if isinstance(array, pandas.Series):
        return set(array.isnull()) == {True}
    temp = []
    return set([is_nan(x) for x in array]) == {True}

def is_nan(x):
    """
    :type x: any value
    """
    if not isinstance(x, float):
        return False
    return pandas.np.isnan(x)


def split(x):
    return CSV_RE.split(x)


def expand_multiple(series):
    index = series.index
    result = (
        expand_base(series)
            .apply(sorted)
            .apply(pandas.Series)
            .reindex(index)
    )
    # Empty special case
    if isinstance(result, pandas.Series):
        return pandas.DataFrame()
    return result

def expand_multiple_bool(series):
    index = series.index
    result = (
        expand_base(series)
           .apply(lambda x: pandas.Series(1, index=x))
           .reindex(index)
           .fillna(0)
           .astype(bool)
    )
    # Empty special case
    if isinstance(result, pandas.Series):
        return pandas.DataFrame()
    return result


def expand_base(series):
    if len(series) == 0:
        return series
    return (
        series
            .dropna()
            .apply(round_cast)
            .apply(six.text_type)
            .apply(text_normalize)
            .str
            .split(r"\s*,\s*")
            .apply(lambda x: map(int_cast, x))
            .apply(set)
        )


def int_cast(x):
    try:
        return int(x)
    except:
        return x


def round_cast(x):
    if not isinstance(x, float):
        return x
    casted = int_cast(x)
    # 1 == 1.0
    if casted == x:
        return casted
    else:
        return x


text_type = six.text_type

def text_normalize(text):
    return unicodedata.normalize("NFKC", text_type(text))


def parse_csv(text):
    return re.split(r"\s*,\s*", text)


def unique_list(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]
