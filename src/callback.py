# -*- coding: utf-8 -*-


class Callback(object):
    def initialize(self, maximum):
        raise NotImplementedError

    def update(self, current):
        raise NotImplementedError

    def finish(self):
        raise NotImplementedError
