# -*- coding: utf-8 -*-

import os

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

if os.name == 'posix':
    font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
elif os.name == 'nt':
    font_path = r'C:\Windows\Fonts\meiryo.ttc'
font_prop = matplotlib.font_manager.FontProperties(fname=font_path)
matplotlib.rcParams['font.family'] = font_prop.get_name()

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(FigureCanvas, self).__init__(self.fig)

