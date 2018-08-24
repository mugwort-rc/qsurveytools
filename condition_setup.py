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
    "includes" : ["sip", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
                  "zmq.backend.cython"],
    "excludes": ["zmq.libzmq"],
    "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe",
                     "libzmq.pyd", "libiomp5md.dll"]
}
setup(
    data_files=matplotlib.get_py2exe_datafiles(),
    options={"py2exe" : py2exe_options},
    windows=[{"script" : "condition.py",
              "dest_base": "conditiontools"}],
    zipfile=None,
)
