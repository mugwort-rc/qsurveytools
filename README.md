# qsurveytools

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Excelでデータ管理を行うことができる集計ツールです。

![mainwindow](./docs/html/html/img/mainwindow-menu.png)

[テンプレートファイル](https://github.com/mugwort-rc/qsurveytools/raw/master/templates/template_ja.xlsx)をもとに設問設定シートに集計したい設問情報を設定し、

![setting](./docs/html/html/img/setting.png)

ソースシートに対応するデータを設定することで単純集計表を出力します。

![source](./docs/html/html/img/source.png)

クロス設定シートにクロスしたい要素を列挙することで、クロス集計表も出力可能です。

![cross](./docs/html/html/img/cross.png)

## Linux

### Install Dependencies

```
pip install -r requirements.txt
```

### Make PyQt files

```
./tools/init-qt-resource.sh
```

### Usage

```
python main.py
```

## Windows

### Install Dependencies

* [WinPython](https://winpython.github.io/)
    * e.g. WinPython 3.6.6.2Qt5-64bit
    * **NOT** Zero Version

### Make PyQt files
