# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import py2exe
from distutils.core import setup

# for py2exe with pandas
# <http://stackoverflow.com/questions/26012182/py2exe-does-not-compile-pandas-read-excel>
import pandas
import matplotlib

py2exe_options = {
    "compressed": 1,
    "optimize": 2,
    "bundle_files": 1,
    "includes" : ["sip", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtGui",
                  "zmq.backend.cython"],
    "excludes": ["zmq.libzmq", "six.moves.urllib", "jsonschema", "nbformat", "jinja2.asyncsupport", "py", "tkinter"],
    "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe",
                     "libzmq.pyd", "libiomp5md.dll"]
}
setup(
    data_files=matplotlib.get_py2exe_datafiles(),
    options={"py2exe" : py2exe_options},
    windows=[{"script" : "main.py",
              "dest_base": "アンケート集計ツール",
              # version
              "version": "2.0.0.0",
              "name": "アンケート集計ツール",
              "copyright": "Copyright (c) 2015-2019 mugwort_rc.",
              "description": "アンケート集計ツール",
              }],
    zipfile=None,
)
