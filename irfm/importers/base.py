# -*- coding: utf-8 -*-


class BaseImporter(object):

    def __init__(self, app):
        self.app = app

    def info(self, msg):
        self.app.logger.info(u'<%s> %s' % (self.__class__.__name__, msg))

    def error(self, msg):
        self.app.logger.error(u'<%s> %s' % (self.__class__.__name__, msg))

    def run(self):
        raise NotImplemented()
