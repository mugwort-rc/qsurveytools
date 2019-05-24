# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication

class Source:
    # Sheets
    @staticmethod
    def sheet_setting():
        return str(QCoreApplication.translate("Source", "Setting"))

    @staticmethod
    def sheet_cross():
        return str(QCoreApplication.translate("Source", "Cross"))

    @staticmethod
    def sheet_source():
        return str(QCoreApplication.translate("Source", "Source"))

    # Setting
    @staticmethod
    def setting_id():
        return str(QCoreApplication.translate("Source", "ID"))

    @staticmethod
    def setting_title():
        return str(QCoreApplication.translate("Source", "TITLE"))

    @staticmethod
    def setting_type():
        return str(QCoreApplication.translate("Source", "TYPE"))

    @staticmethod
    def setting_ok():
        return str(QCoreApplication.translate("Source", "OK"))

    @staticmethod
    def setting_ng():
        return str(QCoreApplication.translate("Source", "NG"))

    # Cross
    @staticmethod
    def cross_sheet():
        return str(QCoreApplication.translate("Source", "Sheets"))

    @staticmethod
    def cross_element():
        return str(QCoreApplication.translate("Source", "Element"))

    @staticmethod
    def cross_element_name():
        return str(QCoreApplication.translate("Source", "ElementName"))


    @classmethod
    def isSettingFrame(cls, frame):
        id_name = cls.setting_id()
        # check first column
        if frame.columns[0] != id_name:
            return False
        if frame[id_name][0] != cls.setting_title():
            return False
        if frame[id_name][1] != cls.setting_type():
            return False
        if frame[id_name][2] != cls.setting_ok():
            return False
        if frame[id_name][3] != cls.setting_ng():
            return False
        return True

    @classmethod
    def isCrossFrame(cls, frame):
        sheet = cls.cross_sheet()
        element = cls.cross_element()
        # check first column,index
        if frame.columns[0] != sheet:
            return False
        if frame.index[0] != element:
            return False
        if frame[sheet][element] != cls.cross_element_name():
            return False
        return True

    @classmethod
    def isSourceFrame(cls, frame):
        id_name = cls.setting_id()
        if frame.columns[0] != id_name:
            return False
        if frame.ix[0][id_name] != cls.setting_title():
            return False
        return True
