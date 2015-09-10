# -*- coding: utf-8 -*-

class ErrorContext(object):

    DEFAULT = 0

    def __init__(self):
        self.current = self.DEFAULT
        self.contexts = {}
        self.indexes = {}

    def clear(self):
        self.current = self.DEFAULT
        self.contexts = {}
        self.indexes = {}

    def setContext(self, context):
        """
        :type context: int
        :param context: current context id
        """
        self.current = context

    def addError(self, id):
        """
        :type id: int or other type
        :param id: user defined type
        """
        # save context
        self.contexts[id] = self.current
        # save index
        if self.current not in self.indexes:
            self.indexes[self.current] = []
        self.indexes[self.current].append(id)

    def errorContext(self, id):
        """
        :type id: int of other type
        :param id: user defined type
        :rtype: int
        """
        if id not in self.contexts:
            return -1
        return self.contexts[id]

    def errorIndex(self, id):
        """
        :type id: int of other type
        :param id: user defined type
        :rtype: int
        :return: index of error context
        """
        ctx = self.errorContext(id)
        if ctx < 0:
            return -1
        return self.indexes[ctx].index(id)
