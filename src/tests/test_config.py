# -*- coding: utf-8 -*-

import os.path

import pandas
import six
import yaml

from .. import config

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "test_data/config.yml")
CONFIG = yaml.load(open(CONFIG_PATH).read())


def test_configbase():
    conf = config.ConfigBase()
    assert isinstance(conf, dict)
    assert dict(conf) == {}

    no_except = True
    try:
        conf.piyo
    except AttributeError:
        no_except = False
    assert no_except == False

    assert hasattr(conf, "piyo") == False

    conf.hoge = "test"
    assert conf.hoge == "test"
    assert dict(conf) == {"hoge":"test"}

    assert hasattr(conf, "hoge") == True


def test_configbase_with_attrs():
    class TestConfig(config.ConfigBase):
        CONFIG = [
            "fuga",  # implicit
            ("fizz", 1),  # explicit
            ("buzz", int),  # explicit (callable)
        ]

    conf = TestConfig()

    no_except = True
    try:
        conf.piyo
    except AttributeError:
        no_except = False
    assert no_except == False

    assert conf.fuga == None
    assert conf.fizz == 1
    assert conf.buzz == int()

    assert dict(conf) == {"fuga": None,
                          "fizz": 1,
                          "buzz": 0}
    conf.piyo = "aaa"
    assert conf.piyo == "aaa"
    assert dict(conf) == {"fuga": None,
                          "fizz": 1,
                          "buzz": 0,
                          "piyo": "aaa"}


def test_make_lambda():
    lmd = config.make_lambda(lambda x: x*3, 3)
    assert lmd() == 9  # default
    assert lmd(2) == 6  # call lambda

def test_make_lambda_map():
    lmd = config.make_lambda_map(lambda x: x*3)
    assert lmd() == []
    assert lmd([1, 2, 3]) == [3, 6, 9]

    lmd = config.make_lambda_map(lambda x: x<<1, [1, 1, 2])
    assert lmd() == [2, 2, 4]
    assert lmd([2, 2, 4], [4, 4, 8])

def test_make_lambda_dict():
    class Dummy:
        def __init__(self, value):
            self.value = value

        def __eq__(self, rhs):
            return isinstance(rhs, Dummy) and self.value == rhs.value

    lmd = config.make_lambda_dict(six.text_type, Dummy)
    assert lmd() == {}
    assert lmd({
        "a": "x",
        1: 0,
    }) == {"a": Dummy("x"), "1": Dummy(0)}

    lmd = config.make_lambda_dict(six.text_type, Dummy, {"a": "z"})
    assert lmd() == {"a":Dummy("z")}
    assert lmd({
        "a": "x",
        1: 0,
    }) == {"a": Dummy("x"), "1": Dummy(0)}


def test_configbase_with_attrs_init():
    class TestConfig(config.ConfigBase):
        CONFIG = [
            ("hoge", str),
            "fuga",
            ("fizz", config.make_lambda(lambda x: x*3, 0)),
            ("buzz", config.make_lambda(lambda x: x*5, 0)),
        ]

    conf = TestConfig({
        "hoge": 1,
        "fuga": 2,
        "fizz": 3,
    })
    assert conf.hoge == "1"
    assert conf.fuga == 2
    assert conf.fizz == 9
    assert conf.buzz == 0


def test_configbase_keys():
    conf = config.ConfigBase()
    assert conf.keys() == []

    # None case
    class TestConfig(config.ConfigBase):
        CONFIG = ["keys"]

    conf = TestConfig()
    assert conf.keys() == ["keys"]

    # value case
    class TestConfig(config.ConfigBase):
        CONFIG = [("keys", "test")]

    conf = TestConfig()
    assert conf.keys() == ["keys"]

    # callable case
    class TestConfig(config.ConfigBase):
        CONFIG = [("keys", int)]

    conf = TestConfig()
    assert conf.keys() == ["keys"]


def test_column():
    column = config.Column()
    assert isinstance(column, config.ConfigBase)

    # check default value
    assert column.type == 0
    assert column.title == ""
    assert column.choice == []
    assert column.noblank == False

def test_column_with_init():
    column = config.Column({
        "type": 1,
        "title": "hello",
        "choice": list("abcdef"),
        "noblank": True,
    })

    # check value
    assert column.type == 1
    assert column.title == "hello"
    assert column.choice == ["a", "b", "c", "d", "e", "f"]
    assert column.noblank == True


def test_column_types():
    column = config.Column({
        "type": "1",
        "title": 123,
        "choice": list(range(1, 5)),
        "noblank": 0,  # bool(0) == False
    })

    # check value
    assert column.type == 1
    assert column.title == "123"
    assert column.choice == ["1", "2", "3", "4"]
    assert column.noblank == False


def test_column_unique_choice():
    column = config.Column({
        "type": 1,
        "title": "hello",
        "choice": list("aabccdeef"),
        "noblank": True,
    })

    # check value
    assert column.choice == ["a", "b", "c", "d", "e", "f"]

    column = config.Column({
        "type": 1,
        "title": "hello",
        "choice": [2, 3, 1, 1, 4, 2, 5],
        "noblank": True,
    })

    # check value
    assert column.choice == ["2", "3", "1", "4", "5"]

    column = config.Column({
        "type": 1,
        "title": "hello",
        "choice": [2, 3, 1, "1", 4, "2", 5],
        "noblank": True,
    })

    # check value
    assert column.choice == ["2", "3", "1", "4", "5"]


def test_filter():
    f = config.Filter()
    assert isinstance(f, config.ConfigBase)

    # check default value
    assert f.key == ""
    assert f.type == ""
    assert f.targets == []
    assert f.choices == []


def test_filter_with_init():
    f = config.Filter({
        "key": "Q1",
        "type": "pickup",
        "targets": ["Q2", 3],
        "choices": [1, 2, "3"]
    })
    assert isinstance(f, config.ConfigBase)

    # check value
    assert f.key == "Q1"
    assert f.type == "pickup"
    assert f.targets == ["Q2", "3"]
    assert f.choices == [1, 2, 3]


def test_filter_types():
    f = config.Filter({
        "key": 123,
        "type": 123,  # ! ERROR USAGE
        "targets": [1, 2],
        "choices": ["1", "2", "3"]
    })

    # check value
    assert f.key == "123"
    assert f.type == "123"
    assert f.targets == ["1", "2"]
    assert f.choices == [1, 2, 3]


def test_crossitem():
    item = config.CrossItem()
    assert isinstance(item, config.ConfigBase)

    # check default value
    assert item.id == ""
    assert item.name == ""


def test_crossitem_with_init():
    item = config.CrossItem({
        "id": "Q1",
        "name": "display name",
    })

    # check value
    assert item.id == "Q1"
    assert item.name == "display name"

    item = config.CrossItem({
        "id": "Q1",
    })
    assert item.id == "Q1"
    assert item.name == ""


def test_crossitem_types():
    item = config.CrossItem({
        "id": 123,
        "name": 321,
    })

    # check value
    assert item.id == "123"
    assert item.name == "321"


def test_cross():
    cross = config.Cross()
    assert isinstance(cross, config.ConfigBase)

    # check default value
    assert cross.keys == []  # special case
    assert cross.targets == []


def test_cross_with_init():
    cross = config.Cross({
        "keys": [
            {"id":"Q1"},],
        "targets": [
            {"id":"Q2"},
            {"id":"Q3"},],
    })

    # check value
    assert len(cross.keys) == 1
    assert len(cross.targets) == 2
    assert isinstance(cross.keys[0], config.CrossItem)
    assert isinstance(cross.targets[0], config.CrossItem)

    assert cross.keys[0].id == "Q1"
    assert cross.targets[1].id == "Q3"


def test_config():
    conf = config.Config(CONFIG)

    # check value
    assert len(conf.columnOrder) == 3
    assert conf.columnOrder == ["Q1", "Q2", "3"]

    assert conf.columns == {
        "Q1": config.Column({
            "choice": ["a", "b", "c", "d"],
            "title": "aaa",
            "type": 1,
        }),
        "Q2": config.Column({
            "choice": ["x", "y", "z"],
            "title": "xxx",
            "type": 2,
        }),
        "3": config.Column({
            "choice": ["1", "2", "3"],
            "title": "111",
            "type": 1,
            "noblank": True,
        }),
    }

    assert len(conf.filters) == 2
    assert conf.filters == [config.Filter({
        "key": "Q1",
        "type": "ignore",
        "choices": ["4"],
        "targets": ["Q2", "3"],
    }), config.Filter({
        "key": "Q2",
        "type": "pickup",
        "choices": ["1", "2"],
        "targets": ["3"],
    })]

    assert conf.cross == config.Cross({
        "keys": [
            config.CrossItem({"id":"Q2"}),
            config.CrossItem({"id":"3", "name":"Q3"}),
        ],
        "targets": [config.CrossItem({"id":"Q1"})],
    })


def test_dump():
    def dump(data):
        return yaml.safe_dump(data, allow_unicode=True, default_flow_style=False)

    conf = config.Config(CONFIG)

    # config.CrossItem
    data = {"id":"3", "name":"Q3"}
    assert config.dump(conf.cross.keys[1]) == dump(data)

    # config.Cross
    data = {
        "keys": [
            {"id":"Q2", "name":""},
            {"id":"3", "name":"Q3"},
        ],
        "targets": [{"id":"Q1", "name":""}],
    }
    assert config.dump(conf.cross) == dump(data)

    # config.Filter
    data = {
        "key": "Q1",
        "type": "ignore",
        "choices": [4],
        "targets": ["Q2", "3"],
    }
    assert config.dump(conf.filters[0]) == dump(data)

    # config.Config
    data = {
        "columnOrder": ["Q1", "Q2", "3"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": 1,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
            "Q2": {
                "choice": ["x", "y", "z"],
                "title": "xxx",
                "type": 2,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
            "3": {
                "choice": ["1", "2", "3"],
                "title": "111",
                "type": 1,
                "noblank": True,
                "limit": 0,
                "multiex": [],
            },
        },
        "filters": [{
            "key": "Q1",
            "type": "ignore",
            "choices": [4],
            "targets": ["Q2", "3"],
        }, {
            "key": "Q2",
            "type": "pickup",
            "choices": [1, 2],
            "targets": ["3"],
        }],
        "cross": {
            "keys": [
                {"id":"Q2", "name":""},
                {"id":"3", "name":"Q3"},
            ],
            "targets": [{"id":"Q1", "name":""}],
        },
    }
    assert config.dump(conf) == dump(data)



def run_test_filter_controller(fc):
    # applyFilter
    frame = pandas.DataFrame([
        [1, "1,2", 1],
        [2, "1,3", 1],
        [3, "3", 1],
        [4, "1,2,3", 1],
    ], columns=["Q1", "Q2", "3"])
    assert len(fc.applyFilter(frame, "Q2")) == 3
    assert len(fc.applyFilter(frame, "3")) == 2

    # isIgnore
    assert not fc.isIgnore(frame, 0, 1)
    assert not fc.isIgnore(frame, 0, 2)
    assert fc.isIgnore(frame, 2, 2)  # by pickup filter
    assert not fc.isIgnore(frame, 3, 0)
    assert fc.isIgnore(frame, 3, 1)  # by ignore filter
    assert fc.isIgnore(frame, 3, 2)


def test_filter_controller():
    conf = config.Config(CONFIG)
    fc = config.FilterController(conf)
    assert len(fc.filter) == 2
    assert len(fc.filter["Q2"]["pickup"]) == 0
    assert len(fc.filter["Q2"]["ignore"]) == 1
    assert len(fc.filter["3"]["pickup"]) == 1
    assert len(fc.filter["3"]["ignore"]) == 1

    run_test_filter_controller(fc)


def test_filter_controller_methods():
    conf = config.Config(CONFIG)
    conf_fc = config.FilterController(conf)
    fc = config.FilterController(config.Config())

    assert len(fc.filter) == 0

    # add methods
    fc.addIgnore("Q2", "Q1", [4])
    assert len(fc.filter) == 1
    assert len(fc.filter["Q2"]["pickup"]) == 0
    assert len(fc.filter["Q2"]["ignore"]) == 1

    fc.addIgnore("3", "Q1", [4])
    assert len(fc.filter) == 2
    assert len(fc.filter["3"]["pickup"]) == 0
    assert len(fc.filter["3"]["ignore"]) == 1

    fc.addPickup("3", "Q2", [1, 2])
    assert len(fc.filter) == 2
    assert len(fc.filter["3"]["pickup"]) == 1
    assert len(fc.filter["3"]["ignore"]) == 1

    assert conf_fc.filter == fc.filter
    fc.typeMap = conf_fc.typeMap

    run_test_filter_controller(fc)

    # edit methods
    assert len(fc.filter["3"]["ignore"]) == 1
    fc.editIgnore("3", 0, "Q2", [3])
    assert len(fc.filter["3"]["ignore"]) == 1
    assert fc.filter["3"]["ignore"][0] == ("Q2", [3])

    assert len(fc.filter["3"]["pickup"]) == 1
    fc.editPickup("3", 0, "Q2", [3])
    assert len(fc.filter["3"]["pickup"]) == 1
    assert fc.filter["3"]["pickup"][0] == ("Q2", [3])

    # duplicate edit
    fc.addIgnore("3", "Q2", [4])  # wrong choices
    assert len(fc.filter["3"]["ignore"]) == 2
    fc.editIgnore("3", 1, "Q2", [3])  # duplicate
    assert len(fc.filter["3"]["ignore"]) == 2  # TODO: remove duplicate
    assert fc.filter["3"]["ignore"][1] == ("Q2", [3])

    fc.addPickup("3", "Q2", [4])  # wrong choices
    assert len(fc.filter["3"]["pickup"]) == 2
    fc.editPickup("3", 1, "Q2", [3])  # duplicate
    assert len(fc.filter["3"]["pickup"]) == 2  # TODO: remove duplicate
    assert fc.filter["3"]["pickup"][1] == ("Q2", [3])

    # remove method
    fc.addIgnore("3", "Q2", [4])  # wrong again
    assert len(fc.filter["3"]["ignore"]) == 3
    fc.removeIgnore("3", 2)
    assert len(fc.filter["3"]["ignore"]) == 2

    fc.addPickup("3", "Q2", [4])  # wrong again
    assert len(fc.filter["3"]["pickup"]) == 3
    fc.removePickup("3", 2)
    assert len(fc.filter["3"]["pickup"]) == 2


def test_make_config_by_data_frame():
    frame = pandas.DataFrame(columns=["ID", "Q1", "Q2", 3],
                             data=[
                                 ["TITLE", "aaa", "xxx", 111],
                                 ["TYPE", "S", "M", "S/NB"],
                                 ["OK", None, None, "Q2=1,2"],
                                 ["NG", None, "Q1=4", "Q1=4"],
                                 [1, "a", "x", 1],
                                 [2, "b", "y", 2],
                                 [3, "c", "z", 3],
                                 [4, "d", None, None],
                                ])
    from numpy import nan
    #       | Sheets | Q1
    # Elems | Name   |
    #    Q2 |        |
    #     3 | Q3     |
    cross = pandas.DataFrame(columns=["Sheets", "Q1"],
                             index=["Elems",
                                    "Q2",
                                    "3"],
                             data=[
                                 ["Name", nan],
                                 [nan, nan],
                                 ["Q3", nan],
                                ])
    f_conf = config.makeConfigByDataFrame(frame, cross)
    y_conf = config.Config(CONFIG)
    assert f_conf.columnOrder == y_conf.columnOrder
    assert f_conf.columns == y_conf.columns

    for f in f_conf.filters:
        assert f in y_conf.filters
    assert f_conf.cross == y_conf.cross


def test_filter_builder():
    conf = config.Config(CONFIG)

    builder = config.FilterBuilder("pickup")
    assert builder.type == "pickup"

    series = pandas.Series([None, None, "Q2=1,2"], index=["Q1", "Q2", 3])
    builder.build(series)

    for f in builder.getFilters():
        assert f in conf.filters

    builder = config.FilterBuilder("ignore")
    assert builder.type == "ignore"

    series = pandas.Series([None, "Q1=4", "Q1=4"], index=["Q1", "Q2", 3])
    builder.build(series)

    for f in builder.getFilters():
        assert f in conf.filters


def test_filter_builder_add_filter():
    conf = config.Config(CONFIG)

    builder = config.FilterBuilder("pickup")
    builder.addFilter("Q2", (1, 2), 3)

    for f in builder.getFilters():
        assert f in conf.filters

    builder = config.FilterBuilder("ignore")
    builder.addFilter("Q1", (4,), "Q2")
    builder.addFilter("Q1", (4,), "3")

    for f in builder.getFilters():
        assert f in conf.filters


def test_parse_filter():
    parsed = list(config.parse_filter_expr("Q1=1&Q2=1,2&Q3=4"))
    assert parsed == [("Q1", (1,)), ("Q2", (1, 2,)), ("Q3", (4,))]

    parsed = list(config.parse_filter_expr("Q1=A"))
    parsed == []


def test_mk_type():
    assert config.mk_type(config.SINGLE) == "S"
    assert config.mk_type(config.MULTIPLE) == "M"
    assert config.mk_type(config.UNKNOWN) == ""

    assert config.mk_type(config.SINGLE, blank=True) == "S/NB"
    assert config.mk_type(config.MULTIPLE, blank=True) == "M/NB"
    assert config.mk_type(config.UNKNOWN, blank=True) == "NB"


def test_get_type():
    assert config.get_type("S") == config.SINGLE
    assert config.get_type("M") == config.MULTIPLE
    assert config.get_type("") == config.UNKNOWN

    # error case
    assert config.get_type(1) == config.UNKNOWN
    assert config.get_type("SM") == config.SINGLE
    assert config.get_type("MS") == config.SINGLE

    # with noblank
    assert config.get_type("S/NB") == config.SINGLE
    assert config.get_type("M/NB") == config.MULTIPLE
    assert config.get_type("NB") == config.UNKNOWN


def test_get_blank():
    assert config.get_blank("S") == False
    assert config.get_blank("M") == False
    assert config.get_blank("") == False

    assert config.get_blank("S/NB") == True
    assert config.get_blank("M/NB") == True
    assert config.get_blank("NB") == True


def test_get_limit():
    assert config.get_limit("") == 0
    assert config.get_limit("S") == 0
    assert config.get_limit("M") == 0
    assert config.get_limit("NB") == 0
    assert config.get_limit("S/NB") == 0
    assert config.get_limit("M/NB") == 0
    assert config.get_limit("M(3)") == 3
    assert config.get_limit("M(4)/NB") == 4
    assert config.get_limit("M[3]") == 0
    assert config.get_limit("M[4]/NB") == 0
    assert config.get_limit("M(3)[4]") == 3
    assert config.get_limit("M(4)[5]/NB") == 4
    assert config.get_limit("M[4](3)") == 3
    assert config.get_limit("M[5](4)/NB") == 4


def test_get_multiex():
    assert config.get_multiex("") == []
    assert config.get_multiex("S") == []
    assert config.get_multiex("M") == []
    assert config.get_multiex("NB") == []
    assert config.get_multiex("S/NB") == []
    assert config.get_multiex("M/NB") == []
    assert config.get_multiex("M(3)") == []
    assert config.get_multiex("M(4)/NB") == []
    assert config.get_multiex("M[3]") == [3]
    assert config.get_multiex("M[4]/NB") == [4]
    assert config.get_multiex("M(3)[4]") == [4]
    assert config.get_multiex("M(4)[5]/NB") == [5]
    assert config.get_multiex("M[4](3)") == [4]
    assert config.get_multiex("M[5](4)/NB") == [5]
    assert config.get_multiex("M[3, 4, 5]") == [3, 4, 5]


def test_mk_filter():
    conf = config.Config(CONFIG)
    fc = config.FilterController(conf)

    assert config.mk_filter(fc.filter["3"]["pickup"]) == "Q2=1,2"
    assert config.mk_filter(fc.filter["Q2"]["ignore"]) == "Q1=4"
    assert config.mk_filter([]) == ""
