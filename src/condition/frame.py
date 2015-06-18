# -*- coding: utf-8 -*-

def byUsedRange(used):
    import pandas
    columns = used[0]
    data = list(used[1:])
    return pandas.DataFrame(data, columns=columns)
