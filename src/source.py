# -*- coding: utf-8 -*-

import os.path

import yaml


class TemplateSetting(object):
    def __init__(self, init={}):
        # check
        if not isinstance(init, dict):
            init = dict()

        # Sheets
        sheets = self._get_dict(init, "Sheets")
        self.sheet_setting = self._get_text(sheets, "Setting")
        self.sheet_cross = self._get_text(sheets, "Cross")
        self.sheet_source = self._get_text(sheets, "Source")

        # Setting
        setting = self._get_dict(init, "Setting")
        self.setting_id = self._get_text(setting, "ID")
        self.setting_title = self._get_text(setting, "TITLE")
        self.setting_type = self._get_text(setting, "TYPE")
        self.setting_ok = self._get_text(setting, "OK")
        self.setting_ng = self._get_text(setting, "NG")

        # Cross
        cross = self._get_dict(init, "Cross")
        self.cross_sheets = self._get_text(cross, "Sheets")
        self.cross_sheet_name = self._get_text(cross, "SheetName")
        self.cross_element = self._get_text(cross, "Element")
        self.cross_element_name = self._get_text(cross, "ElementName")

        # Source
        source = self._get_dict(init, "Source")
        self.source_id = self._get_text(source, "ID")
        self.source_title = self._get_text(source, "TITLE")

    def _get_dict(self, data, key):
        result = data.get(key, {})
        if not isinstance(result, dict):
            return dict()
        return result

    def _get_text(self, data, key):
        return data.get(key, key)

    def sheet_names(self):
        return [self.sheet_setting, self.sheet_cross, self.sheet_source]

    @staticmethod
    def from_yaml(fp):
        if fp is not None:
            if not hasattr(fp, "read"):
                if os.path.exists(fp):
                    fp = open(fp)
                else:
                    fp = None
        if fp is not None:
            data = yaml.load(fp.read())
        else:
            data = {}

        return TemplateSetting(data)
