# -*- coding: utf-8 -*-

import re
import types

import yaml
from yaml.dumper import SafeDumper
from yaml.representer import SafeRepresenter

from . import utils
from .utils import and_concat, or_concat
from .utils import expand_multiple_bool

UNKNOWN = 0
SINGLE = 1
MULTIPLE = 2
FREE = 3

class ConfigBase(dict):

    # CONFIG
    # ["name1", "name2", ...]
    #   Config.name1 = None
    #   Config.name2 = None
    # or
    # [("name1", init), ("name2", init), ...]
    #   Config.name1 = init()
    #   Config.name2 = init()
    CONFIG = []

    def __init__(self, base={}, **kwargs):
        if kwargs:
            base.update(kwargs)
        self.update(base)
        for attr in self.CONFIG:
            if isinstance(attr, tuple) and len(attr) == 2:
                key, default = attr
                if callable(default):
                    if key in self:
                        setattr(self, key, default(self[key]))
                    else:
                        setattr(self, key, default())
                else:
                    setattr(self, key, default)
            elif attr not in self:
                setattr(self, attr, None)

    def __getattr__(self, key):
        # CONFIG special case
        if key == "CONFIG":
            return self.CONFIG
        if key not in self:
            raise AttributeError
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


def make_lambda(func, default):
    return lambda *args: func(args[0]) if args else func(default)

def _lambda_chain(f1, f2, default):
    return make_lambda(lambda x: f2(f1(x)), [])

def make_lambdas(funcs, default):
    assert isinstance(funcs, list)
    assert len(funcs) > 0
    result = funcs[0]
    for func in funcs[1:]:
        result = _lambda_chain(result, func, default)
    return result

def make_lambda_map(type, default=[]):
    return make_lambda(lambda x: list(map(type, x)), default)

def make_lambda_dict(ktype, vtype, default={}):
    _gen = lambda x: _gen_type_dict(ktype, vtype, x)
    return make_lambda(_gen, default)

def _gen_type_dict(ktype, vtype, d):
    return {ktype(k):vtype(v) for k,v in d.items()}

make_unique = make_lambda(utils.unique_list, [])


class Config(ConfigBase):

    CONFIG = [
        ("columnOrder", make_lambda_map(str)),
        # lazy eval (lambda x: ...)
        ("columns", make_lambda_dict(str, lambda x: Column(x))),
        ("filters", make_lambda_map(lambda x: Filter(x))),
        ("cross", make_lambda(lambda x: Cross(x), {})),]


_make_column_choice = make_lambdas([make_lambda_map(str), make_unique], [])
_make_multiex = make_lambdas([make_lambda_map(int), make_unique], [])

class Column(ConfigBase):
    CONFIG = [
        ("type", int),
        ("title", str),
        ("choice", _make_column_choice),
        ("complete", bool),
        ("limit", int),
        ("multiex", _make_multiex),]

class Filter(ConfigBase):

    CONFIG = [
        ("key", str),
        ("type", str),
        ("targets", make_lambda_map(str)),
        ("choices", make_lambda_map(int)),]

    def __unicode__(self):
        return '<{}:"{}" [{}]>: {}'.format(
            self.type, self.key,
            ', '.join(map(str, self.choices)),
            ', '.join(map(lambda x: '"{}"'.format(x), self.targets))
        )


lambda_cross_item = make_lambda_map(lambda x: CrossItem(x))  # lazy eval

class Cross(ConfigBase):

    CONFIG = [
        ("keys", lambda_cross_item),
        ("targets", lambda_cross_item),]

    def setKey(self, item):
        try:
            index = [x.id for x in self.keys].index(item.id)
            self.keys[index] = item
        except ValueError:
            self.keys.append(item)

    def setTarget(self, item):
        try:
            index = [x.id for x in self.targets].index(item.id)
            self.targets[index] = item
        except ValueError:
            self.targets.append(item)

    @property
    def keys(self):
        return self.get("keys")

class CrossItem(ConfigBase):

    CONFIG = [
        ("id", str),
        ("name", str),]

    def __unicode__(self):
        return '<{}>'.format(self.name if self.name else '#{}'.format(self.id))

    @staticmethod
    def by_id(id):
        return CrossItem({'id': id})

    @staticmethod
    def by_id_with_name(id, name):
        return CrossItem({'id': id, 'name': name})


SafeDumper.add_representer(Config, SafeRepresenter.represent_dict)
SafeDumper.add_representer(Column, SafeRepresenter.represent_dict)
SafeDumper.add_representer(Filter, SafeRepresenter.represent_dict)
SafeDumper.add_representer(Cross, SafeRepresenter.represent_dict)
SafeDumper.add_representer(CrossItem, SafeRepresenter.represent_dict)

def dump(data):
    return yaml.dump(data,
                     allow_unicode=True,
                     default_flow_style=False,
                     Dumper=SafeDumper)


class FilterController(object):
    def __init__(self, config):
        self.filter = {}
        self.typeMap = {}
        for column in config.columns:
            conf = config.columns[column]
            self.typeMap[column] = conf.get('type', UNKNOWN)
        # expand filter config
        for filter in config.filters:
            for target in filter.targets:
                choices = filter.choices
                self._add(target, filter.type, filter.key, choices)

    def _add(self, target, mode, key, values):
        if target not in self.filter:
            self.filter[target] = {
                'pickup': [],
                'ignore': [],
            }
        self.filter[target][mode].append((key, values))

    def _edit(self, target, mode, index, key, values):
        self.filter[target][mode][index] = (key,values)

    def _remove(self, target, mode, index):
        del self.filter[target][mode][index]

    def addPickup(self, target, key, values):
        self._add(target, 'pickup', key, values)

    def addIgnore(self, target, key, values):
        self._add(target, 'ignore', key, values)

    def editPickup(self, target, index, key, values):
        self._edit(target, 'pickup', index, key, values)

    def editIgnore(self, target, index, key, values):
        self._edit(target, 'ignore', index, key, values)

    def removePickup(self, target, index):
        self._remove(target, 'pickup', index)

    def removeIgnore(self, target, index):
        self._remove(target, 'ignore', index)

    def applyFilter(self, frame, column, extend_refs=False, applied=None):
        if applied is None:
            applied = list()
        # check applied
        if column in applied:
            return frame
        else:
            applied.append(column)
        # check config existing
        if column not in self.filter:
            return frame
        # get filter
        filter = self.filter[column]
        conds = []
        refs = []
        # get pickup filters
        for ref,values in filter['pickup']:
            if ref not in refs:
                refs.append(ref)
            type = self.typeMap.get(ref, UNKNOWN)
            if type != MULTIPLE:
                conds.append(frame[ref].isin(values))
            else:
                multiple = expand_multiple_bool(frame[ref])
                m_conds = []
                for value in values:
                    if value not in multiple.columns:
                        continue
                    m_conds.append(multiple[value])
                if m_conds:
                    conds.append(or_concat(m_conds))
                else:
                    return frame[:0]  # Empty DataFrame
        # get ignore filters
        for ref,values in filter['ignore']:
            if ref not in refs:
                refs.append(ref)
            type = self.typeMap.get(ref, UNKNOWN)
            if type != MULTIPLE:
                conds.append(~frame[ref].isin(values))
            else:
                multiple = expand_multiple_bool(frame[ref])
                m_conds = []
                for value in values:
                    if value not in multiple.columns:
                        continue  # no filter
                    m_conds.append(~multiple[value])
                if m_conds:
                    conds.append(or_concat(m_conds))
        # check filters
        if not conds:
            return frame
        # extend to ref columns
        frame = frame[and_concat(conds)]
        if extend_refs:
            for ref in refs:
                frame = self.applyFilter(frame, ref, extend_refs=extend_refs, applied=applied)
        return frame

    def isIgnore(self, frame, row, column):
        index = frame.index[row]
        column = frame.columns[column]
        if column not in self.filter:
            return False
        for ref,values in self.filter[column]['ignore']:
            type = self.typeMap.get(ref, 0)
            if type != MULTIPLE:
                if frame[ref][index] in values:
                    return True
            else:
                values = map(str, values)
                data = utils.split(str(frame[ref][index]))
                for value in values:
                    if value in data:
                        return True
        for ref,values in self.filter[column]['pickup']:
            type = self.typeMap.get(ref, 0)
            if type != MULTIPLE:
                if frame[ref][index] not in values:
                    return True
            else:
                values = map(str, values)
                data = utils.split(str(frame[ref][index]))
                for value in values:
                    if value in data:
                        return False  # found
                return True  # not found
        return False


class ConfigCallback(object):
    def duplicatedChoice(self, column):
        raise NotImplementedError

    def reservedChoice(self, column):
        raise NotImplementedError


def makeConfigByDataFrame(frame, cross=None, cb=None, reserved=[]):
    if cb is not None:
        assert isinstance(cb, ConfigCallback)
    # columns
    assert(frame.columns[0] == 'ID')
    del frame['ID']
    # drop auto generated columns
    for col in frame.columns:
        if not isinstance(col, str):
            continue
        # special case for pandas.read_excel and win32.byUsedRange
        if not is_auto_generated(col):
            continue
        del frame[col]
    columns = frame.columns.tolist()
    TITLE  = 0
    TYPE   = 1
    OK     = 2
    NG     = 3
    START = 3 + 1
    def get_row(idx):
        return frame.ix[idx]
    # title series
    titles = get_row(TITLE)
    # type series
    types = get_row(TYPE)
    # filter OK
    ok = get_row(OK).dropna()
    # filter NG
    ng = get_row(NG).dropna()
    # choice frame
    choices = frame[START:]

    # generate config by frame
    config = Config()
    # columnOrder
    config.columnOrder = list(map(str, columns))
    # columns
    for rawcol, strcol in zip(columns, config.columnOrder):
        # skip empty column
        if rawcol is None:
            continue
        column_config = Column({
            'type': get_type(types[rawcol]),
            'complete': get_complete(types[rawcol]),
            'limit': get_limit(types[rawcol]),
            'multiex': get_multiex(types[rawcol]),
            'title': str(titles[rawcol]),
            'choice': list(map(str, choices[rawcol].dropna().values.tolist())),
        })
        if cb is not None:
            for choice in choices[rawcol].dropna():
                if choice in reserved:
                    cb.reservedChoice(rawcol)
            if len(column_config["choice"]) != len(choices[rawcol].dropna()):
                cb.duplicatedChoice(rawcol)
        config.columns[strcol] = column_config

    # filter
    pickup = FilterBuilder('pickup')
    pickup.build(ok)
    ignore = FilterBuilder('ignore')
    ignore.build(ng)
    config.filters = list(pickup.getFilters()) + list(ignore.getFilters())

    # cross
    if cross is not None:
        keys, targets = makeCrossByDataFrame(cross)
        # column side
        config.cross.targets = targets
        # index side
        config.cross.keys = keys
    return config

def makeCrossByDataFrame(frame):
    import numpy
    def is_empty(value):
        if value is None:
            return True
        if isinstance(value, float) and numpy.isnan(value):
            return True
        return False

    def gen_cross_item(key, name):
        if is_empty(name):
            return CrossItem.by_id(key)
        return CrossItem.by_id_with_name(key, name)

    def get_cross_series(frame):
        first = frame.columns[0]
        return frame[1:][first]

    keys = get_cross_series(frame)
    targets = get_cross_series(frame.T)

    def series_to_items(series):
        return [gen_cross_item(index, series[index]) for index in series.index if not is_empty(index) and not is_auto_generated(index)]

    return series_to_items(keys), series_to_items(targets)


def is_auto_generated(name):
    # special case for pandas.read_excel and win32.byUsedRange
    return name.startswith("Unnamed:") or name.startswith("None.")


class FilterBuilder(object):
    def __init__(self, type):
        """
        :param str type: 'pickup' or 'ignore'
        """
        #assert(type in ['pickup', 'ignore'])
        self.type = type
        self.registry = {}
        self.error = []

    def build(self, series):
        """
        :param pandas.Series series: filter series
        """
        series = series.dropna()
        for target in series.index:
            for key,values in parse_filter_expr(series[target]):
                self.addFilter(key, values, target)

    def addFilter(self, key, values, target):
        """
        :type key: str
        :param key: filter key (source)
        :type values: tuple[int]
        :param values: filter values
        :type target: str
        :param target: filter (apply) target
        """
        #assert(isinstance(values, tuple))
        if (key, values) not in self.registry:
            self.registry[(key,values)] = []
        if target not in self.registry[(key,values)]:
            self.registry[(key,values)].append(target)

    def getFilters(self):
        """
        :rtype: iter
        :return: filter yield iterator
        """
        for (key,values), targets in self.registry.items():
            yield Filter({
                'key': key,
                'choices': list(values),
                'type': self.type,
                'targets': targets,
            })


def parse_filter_expr(src):
    """
    :type src: str
    :param src: expr text
    :rtype: generator[tuple[str, tuple[int]]]
    :return: parsed key-values
    """
    import re
    for item in re.split(r'\s*&\s*', src):
        m = re.match(r'^([^=]+)\s*=\s*(.+)$', item.strip())
        if m:
            key = m.group(1)
            rhs = m.group(2)
            values = [int(x.strip()) for x in rhs.split(',') if re.match('^\d+$', x.strip())]
            yield (key, tuple(values))


def mk_type(type, complete=False):
    temp = []
    if type == SINGLE:
        temp.append('S')
    elif type == MULTIPLE:
        temp.append('M')
    elif type == FREE:
        temp.append('F')
    if complete:
        temp.append('C')
    return '/'.join(temp)

def get_type(type):
    if not isinstance(type, str):
        return UNKNOWN
    type = utils.text_normalize(type)
    if 'F' in type:
        return FREE
    elif 'S' in type:
        return SINGLE
    elif 'M' in type:
        return MULTIPLE
    return UNKNOWN

def get_complete(type):
    if isinstance(type, str):
        type = utils.text_normalize(type)
        return 'C' in type
    return False

def get_limit(type):
    if get_type(type) != MULTIPLE:
        return 0
    type = utils.text_normalize(type)
    m = re.search(r"M\s*(?:\[[^\]]+\]\s*)?\(\s*(\d+)\s*\)", type)
    if not m:
        return 0
    return int(m.group(1))

def get_multiex(type):
    if get_type(type) != MULTIPLE:
        return []
    type = utils.text_normalize(type)
    m = re.search(r"M\s*(?:\(\s*\d+\s*\))?\[\s*(\d+(\s*,\s*\d+)*)\s*\]", type)
    if not m:
        return []
    result = []
    for value in utils.parse_csv(m.group(1)):
        try:
            result.append(int(value))
        except:
            continue
    return utils.unique_list(result)


def mk_filter(column_config):
    """
    see also FilterController.filter[name][type]

    :type column_config: list[str, tuple[int]]
    :param column_config: filter setting of one column
    :rtype: str
    :return: filter expr text
    """
    temp = []
    for key,values in column_config:
        temp.append("{}={}".format(key, ",".join(map(str, values))))
    return "&".join(temp)
