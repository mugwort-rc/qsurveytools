# -*- coding: utf-8 -*-

import mock
import pandas
import six


from .. import config
from .. import validator


def make_config():
    return config.Config({
        "columnOrder": ["Q1", "Q2"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.SINGLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
            "Q2": {
                "choice": ["x", "y", "z"],
                "title": "xxx",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
        "filters": [{
            "key": "Q1",
            "type": "ignore",
            "choices": [4],
            "targets": ["Q2"],
        }],
    })


def test_progress_functions():
    conf = config.Config({
        "columnOrder": ["Q1", "Q2"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.SINGLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
            "Q2": {
                "choice": ["x", "y", "z"],
                "title": "xxx",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
    })
    frame = pandas.DataFrame()
    cb = mock.MagicMock()
    
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    # initialize
    assert cb.initialize.called
    assert cb.initialize.call_count == 1
    assert cb.initialize.call_args == ((2,),)

    # update
    assert cb.update.called
    assert cb.update.call_count == 2
    assert cb.update.call_args_list == [((0,),), ((1,),)]

    # finalize
    assert cb.finish.called
    assert cb.finish.call_count == 1
    assert cb.finish.call_args == tuple()


def test_not_found_in_frame():
    conf = make_config()
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [2],
            [3],
            [4],
        ])
    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.columnNotFound.called
    assert cb.columnNotFound.call_count == 1
    assert cb.columnNotFound.call_args == (("Q2",),)


def test_setting_is_unknown():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.UNKNOWN,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
    })
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [2],
            [3],
            [4],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.settingIsUnknown.called
    assert cb.settingIsUnknown.call_count == 1
    assert cb.settingIsUnknown.call_args == (("Q1",),)


def test_setting_free_answer():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.FREE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
    })
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [2],
            [3],
            [4],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert not cb.settingIsUnknown.called


def test_validation_error_single():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.SINGLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
    })

    # without ID
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [3],
            [5],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 2, 5, id=None)

    # with ID
    frame = pandas.DataFrame(columns=["ID", "Q1"],
        data=[
            ["x", 1],
            ["y", 3],
            ["z", 5],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 2, 5, id="z")



def test_validation_error_multiple_simple():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
    })

    # without ID
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [3],
            [5],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 2, 5, id=None)

    # with ID
    frame = pandas.DataFrame(columns=["ID", "Q1"],
        data=[
            ["x", 1],
            ["y", 3],
            ["z", 5],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 2, 5, id="z")


def test_validation_error_multiple_csv():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 0,
                "multiex": [],
            },
        },
    })

    # without ID
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            ["1,3,5"],
            [3],
            ["3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 0, 5, id=None)

    # with ID
    frame = pandas.DataFrame(columns=["ID", "Q1"],
        data=[
            ["x", "1,3,5"],
            ["y", 3],
            ["z", "3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 0, 5, id="x")


def test_multiple_exception_error_for_single():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.SINGLE,
                "noblank": False,
                "limit": 0,
                "multiex": [1,2],  # wrong
            },
        },
    })

    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [3],
            [5],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert not cb.multipleExceptionError.called


def test_multiple_exception_error_for_multiple():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 0,
                "multiex": [1,2],
            },
        },
    })

    # without ID
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            ["1,3,5"],
            [3],
            ["3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.multipleExceptionError.called
    assert cb.multipleExceptionError.call_count == 1
    assert cb.multipleExceptionError.call_args == mock.call("Q1", 0, "1,3,5", id=None)

    # with ID
    frame = pandas.DataFrame(columns=["ID", "Q1"],
        data=[
            ["x", "1,3,5"],
            ["y", 3],
            ["z", "3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.multipleExceptionError.called
    assert cb.multipleExceptionError.call_count == 1
    assert cb.multipleExceptionError.call_args == mock.call("Q1", 0, "1,3,5", id="x")


def test_limitation_error_for_single():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.SINGLE,
                "noblank": False,
                "limit": 2,  # wrong
                "multiex": [],
            },
        },
    })

    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            [1],
            [3],
            [5],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert not cb.limitationError.called


def test_limitation_error_for_multiple():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 2,
                "multiex": [],
            },
        },
    })

    # without ID
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            ["1,3,5"],
            [3],
            ["3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.limitationError.called
    assert cb.limitationError.call_count == 1
    assert cb.limitationError.call_args == mock.call("Q1", 0, "1,3,5", id=None)

    # with ID
    frame = pandas.DataFrame(columns=["ID", "Q1"],
        data=[
            ["x", "1,3,5"],
            ["y", 3],
            ["z", "3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.limitationError.called
    assert cb.limitationError.call_count == 1
    assert cb.limitationError.call_args == mock.call("Q1", 0, "1,3,5", id="x")


def test_multiple_errors():
    conf = config.Config({
        "columnOrder": ["Q1"],
        "columns": {
            "Q1": {
                "choice": ["a", "b", "c", "d"],
                "title": "aaa",
                "type": config.MULTIPLE,
                "noblank": False,
                "limit": 2,
                "multiex": [4],
            },
        },
    })

    # without ID
    frame = pandas.DataFrame(columns=["Q1"],
        data=[
            ["1,3,5"],
            [3],
            ["3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 0, 5, id=None)

    assert cb.multipleExceptionError.called
    assert cb.multipleExceptionError.call_count == 1
    assert cb.multipleExceptionError.call_args == mock.call("Q1", 2, "3,4", id=None)

    assert cb.limitationError.called
    assert cb.limitationError.call_count == 1
    assert cb.limitationError.call_args == mock.call("Q1", 0, "1,3,5", id=None)

    # with ID
    frame = pandas.DataFrame(columns=["ID", "Q1"],
        data=[
            ["x", "1,3,5"],
            ["y", 3],
            ["z", "3,4"],
        ])

    cb = mock.MagicMock()
    v = validator.ValidationObject(cb, conf)
    v.validate(frame)

    assert cb.validationError.called
    assert cb.validationError.call_count == 1
    assert cb.validationError.call_args == mock.call("Q1", 0, 5, id="x")

    assert cb.multipleExceptionError.called
    assert cb.multipleExceptionError.call_count == 1
    assert cb.multipleExceptionError.call_args == mock.call("Q1", 2, "3,4", id="z")

    assert cb.limitationError.called
    assert cb.limitationError.call_count == 1
    assert cb.limitationError.call_args == mock.call("Q1", 0, "1,3,5", id="x")
