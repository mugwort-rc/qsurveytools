# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui_mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(446, 295)
        MainWindow.setToolTip("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_3.addWidget(self.progressBar, 2, 1, 1, 1)
        self.horizontalLayoutMenuButtons = QtWidgets.QHBoxLayout()
        self.horizontalLayoutMenuButtons.setObjectName("horizontalLayoutMenuButtons")
        spacerItem = QtWidgets.QSpacerItem(90, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutMenuButtons.addItem(spacerItem)
        self.pushButtonSimple = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonSimple.setObjectName("pushButtonSimple")
        self.horizontalLayoutMenuButtons.addWidget(self.pushButtonSimple)
        self.pushButtonCross = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonCross.setObjectName("pushButtonCross")
        self.horizontalLayoutMenuButtons.addWidget(self.pushButtonCross)
        self.gridLayout_3.addLayout(self.horizontalLayoutMenuButtons, 3, 0, 1, 2)
        self.progressBarGeneral = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBarGeneral.setProperty("value", 24)
        self.progressBarGeneral.setObjectName("progressBarGeneral")
        self.gridLayout_3.addWidget(self.progressBarGeneral, 1, 1, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabMenu = QtWidgets.QWidget()
        self.tabMenu.setObjectName("tabMenu")
        self.gridLayout = QtWidgets.QGridLayout(self.tabMenu)
        self.gridLayout.setObjectName("gridLayout")
        self.labelInput = QtWidgets.QLabel(self.tabMenu)
        self.labelInput.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelInput.setObjectName("labelInput")
        self.gridLayout.addWidget(self.labelInput, 0, 0, 1, 1)
        self.toolButtonOutput = QtWidgets.QToolButton(self.tabMenu)
        self.toolButtonOutput.setObjectName("toolButtonOutput")
        self.gridLayout.addWidget(self.toolButtonOutput, 1, 2, 1, 1)
        self.lineEditOutput = QtWidgets.QLineEdit(self.tabMenu)
        self.lineEditOutput.setObjectName("lineEditOutput")
        self.gridLayout.addWidget(self.lineEditOutput, 1, 1, 1, 1)
        self.labelOutput = QtWidgets.QLabel(self.tabMenu)
        self.labelOutput.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelOutput.setObjectName("labelOutput")
        self.gridLayout.addWidget(self.labelOutput, 1, 0, 1, 1)
        self.toolButtonInput = QtWidgets.QToolButton(self.tabMenu)
        self.toolButtonInput.setObjectName("toolButtonInput")
        self.gridLayout.addWidget(self.toolButtonInput, 0, 2, 1, 1)
        self.lineEditInput = QtWidgets.QLineEdit(self.tabMenu)
        self.lineEditInput.setDragEnabled(False)
        self.lineEditInput.setObjectName("lineEditInput")
        self.gridLayout.addWidget(self.lineEditInput, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 3)
        self.tabWidget.addTab(self.tabMenu, "")
        self.tabMessage = QtWidgets.QWidget()
        self.tabMessage.setObjectName("tabMessage")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tabMessage)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.listView = QtWidgets.QListView(self.tabMessage)
        self.listView.setObjectName("listView")
        self.gridLayout_2.addWidget(self.listView, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabMessage, "")
        self.tabSetting = QtWidgets.QWidget()
        self.tabSetting.setObjectName("tabSetting")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tabSetting)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidgetSetting = QtWidgets.QTabWidget(self.tabSetting)
        self.tabWidgetSetting.setObjectName("tabWidgetSetting")
        self.tabGeneral = QtWidgets.QWidget()
        self.tabGeneral.setObjectName("tabGeneral")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tabGeneral)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.checkBoxDropNA = QtWidgets.QCheckBox(self.tabGeneral)
        self.checkBoxDropNA.setObjectName("checkBoxDropNA")
        self.gridLayout_4.addWidget(self.checkBoxDropNA, 0, 0, 1, 1)
        self.checkBoxExtendFilter = QtWidgets.QCheckBox(self.tabGeneral)
        self.checkBoxExtendFilter.setChecked(False)
        self.checkBoxExtendFilter.setObjectName("checkBoxExtendFilter")
        self.gridLayout_4.addWidget(self.checkBoxExtendFilter, 0, 1, 1, 1)
        self.checkBoxWithPercent = QtWidgets.QCheckBox(self.tabGeneral)
        self.checkBoxWithPercent.setChecked(True)
        self.checkBoxWithPercent.setObjectName("checkBoxWithPercent")
        self.gridLayout_4.addWidget(self.checkBoxWithPercent, 1, 0, 1, 1)
        self.tabWidgetSetting.addTab(self.tabGeneral, "")
        self.tabError = QtWidgets.QWidget()
        self.tabError.setObjectName("tabError")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tabError)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.checkBoxAggregateError = QtWidgets.QCheckBox(self.tabError)
        self.checkBoxAggregateError.setObjectName("checkBoxAggregateError")
        self.gridLayout_5.addWidget(self.checkBoxAggregateError, 0, 0, 1, 1)
        self.checkBoxIgnoreForbiddenError = QtWidgets.QCheckBox(self.tabError)
        self.checkBoxIgnoreForbiddenError.setChecked(True)
        self.checkBoxIgnoreForbiddenError.setObjectName("checkBoxIgnoreForbiddenError")
        self.gridLayout_5.addWidget(self.checkBoxIgnoreForbiddenError, 1, 0, 1, 1)
        self.tabWidgetSetting.addTab(self.tabError, "")
        self.tabSimple = QtWidgets.QWidget()
        self.tabSimple.setObjectName("tabSimple")
        self.formLayout_3 = QtWidgets.QFormLayout(self.tabSimple)
        self.formLayout_3.setObjectName("formLayout_3")
        self.checkBoxSAToPie = QtWidgets.QCheckBox(self.tabSimple)
        self.checkBoxSAToPie.setObjectName("checkBoxSAToPie")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkBoxSAToPie)
        self.tabWidgetSetting.addTab(self.tabSimple, "")
        self.tabCross = QtWidgets.QWidget()
        self.tabCross.setObjectName("tabCross")
        self.formLayout = QtWidgets.QFormLayout(self.tabCross)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.labelCrossTableStyle = QtWidgets.QLabel(self.tabCross)
        self.labelCrossTableStyle.setObjectName("labelCrossTableStyle")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labelCrossTableStyle)
        self.comboBoxCrossFormat = QtWidgets.QComboBox(self.tabCross)
        self.comboBoxCrossFormat.setObjectName("comboBoxCrossFormat")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBoxCrossFormat)
        self.checkBoxChartAddYTotal = QtWidgets.QCheckBox(self.tabCross)
        self.checkBoxChartAddYTotal.setObjectName("checkBoxChartAddYTotal")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.checkBoxChartAddYTotal)
        self.checkBoxChartDropYBlank = QtWidgets.QCheckBox(self.tabCross)
        self.checkBoxChartDropYBlank.setObjectName("checkBoxChartDropYBlank")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.checkBoxChartDropYBlank)
        self.tabWidgetSetting.addTab(self.tabCross, "")
        self.tabAnalyze = QtWidgets.QWidget()
        self.tabAnalyze.setObjectName("tabAnalyze")
        self.formLayout_2 = QtWidgets.QFormLayout(self.tabAnalyze)
        self.formLayout_2.setObjectName("formLayout_2")
        self.checkBoxAnalyzeAbstract = QtWidgets.QCheckBox(self.tabAnalyze)
        self.checkBoxAnalyzeAbstract.setChecked(False)
        self.checkBoxAnalyzeAbstract.setObjectName("checkBoxAnalyzeAbstract")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkBoxAnalyzeAbstract)
        self.checkBoxCellEmphasis = QtWidgets.QCheckBox(self.tabAnalyze)
        self.checkBoxCellEmphasis.setObjectName("checkBoxCellEmphasis")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.checkBoxCellEmphasis)
        self.tabWidgetSetting.addTab(self.tabAnalyze, "")
        self.tabData = QtWidgets.QWidget()
        self.tabData.setObjectName("tabData")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.tabData)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.pushButtonExpand = QtWidgets.QPushButton(self.tabData)
        self.pushButtonExpand.setObjectName("pushButtonExpand")
        self.gridLayout_6.addWidget(self.pushButtonExpand, 0, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem2, 0, 2, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_6.addItem(spacerItem3, 2, 1, 1, 1)
        self.checkBoxRaw = QtWidgets.QCheckBox(self.tabData)
        self.checkBoxRaw.setObjectName("checkBoxRaw")
        self.gridLayout_6.addWidget(self.checkBoxRaw, 1, 1, 1, 1)
        self.tabWidgetSetting.addTab(self.tabData, "")
        self.verticalLayout.addWidget(self.tabWidgetSetting)
        self.tabWidget.addTab(self.tabSetting, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 446, 24))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidgetSetting.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButtonSimple.setText(_translate("MainWindow", "Simple"))
        self.pushButtonCross.setText(_translate("MainWindow", "Cross"))
        self.labelInput.setText(_translate("MainWindow", "Input"))
        self.toolButtonOutput.setText(_translate("MainWindow", "..."))
        self.lineEditOutput.setPlaceholderText(_translate("MainWindow", "Output"))
        self.labelOutput.setText(_translate("MainWindow", "Output"))
        self.toolButtonInput.setText(_translate("MainWindow", "..."))
        self.lineEditInput.setPlaceholderText(_translate("MainWindow", "Input"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMenu), _translate("MainWindow", "Menu"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMessage), _translate("MainWindow", "Message"))
        self.checkBoxDropNA.setText(_translate("MainWindow", "Drop N/A"))
        self.checkBoxExtendFilter.setText(_translate("MainWindow", "Extend Filter"))
        self.checkBoxWithPercent.setText(_translate("MainWindow", "with %"))
        self.tabWidgetSetting.setTabText(self.tabWidgetSetting.indexOf(self.tabGeneral), _translate("MainWindow", "General"))
        self.checkBoxAggregateError.setText(_translate("MainWindow", "Aggregate Error"))
        self.checkBoxIgnoreForbiddenError.setText(_translate("MainWindow", "Ignore forbidden errors"))
        self.tabWidgetSetting.setTabText(self.tabWidgetSetting.indexOf(self.tabError), _translate("MainWindow", "Error"))
        self.checkBoxSAToPie.setText(_translate("MainWindow", "SA to Pie"))
        self.tabWidgetSetting.setTabText(self.tabWidgetSetting.indexOf(self.tabSimple), _translate("MainWindow", "Simple"))
        self.labelCrossTableStyle.setText(_translate("MainWindow", "TableStyle"))
        self.checkBoxChartAddYTotal.setText(_translate("MainWindow", "[Chart] Add Y Total"))
        self.checkBoxChartDropYBlank.setText(_translate("MainWindow", "[Chart] Drop Y Blank"))
        self.tabWidgetSetting.setTabText(self.tabWidgetSetting.indexOf(self.tabCross), _translate("MainWindow", "Cross"))
        self.checkBoxAnalyzeAbstract.setText(_translate("MainWindow", "Insert abstract information"))
        self.checkBoxCellEmphasis.setText(_translate("MainWindow", "Cell emphasis"))
        self.tabWidgetSetting.setTabText(self.tabWidgetSetting.indexOf(self.tabAnalyze), _translate("MainWindow", "Analyze"))
        self.pushButtonExpand.setText(_translate("MainWindow", "Expand"))
        self.checkBoxRaw.setText(_translate("MainWindow", "Raw output"))
        self.tabWidgetSetting.setTabText(self.tabWidgetSetting.indexOf(self.tabData), _translate("MainWindow", "Data"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSetting), _translate("MainWindow", "Setting"))


import qsurveytools_rc
