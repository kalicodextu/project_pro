#!/usr/bin/python
# -*- coding: utf-8 -*-
import gevent
from gevent import monkey
monkey.patch_all()

from datetime import datetime

from json import loads
from xybase.database import MongoDBBase
from xybase.utils.util_base import UtilBase
from settings import config, logger


class TaskException(Exception):
    def __init__(self, value):
        super(TaskException, self).__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)


class StorageTask(UtilBase):
    def __init__(self, config):
        self.config = config
        self.storage = MongoDBBase(self.config)

    def getConnections(self):
        url = self.config.get('connectionsUrl')
        count = 0
        while count < 3:
            try:
                resp = self.request('GET', url)
            except Exception:
                count += 1
                gevent.sleep(5)
                continue
            if resp.status_code == 200:
                content_dict = loads(resp.content)
                if content_dict.has_key('ESTABLISHED'):
                    return content_dict.get('ESTABLISHED')
                else:
                    raise TaskException(
                        'Connections Service Has No Key: ESTABLISHED.')
            else:
                gevent.sleep(5)
                count += 1
                continue
        raise TaskException('Access Connections Service Failed.')

    def storageTask(self):
        while True:
            try:
                querytime = str(datetime.utcnow())
                connections = self.getConnections()
            except TaskException as ex:
                data = {'connCount': -1, 'queryTime': querytime, 'errorDesc': str(ex)}
                self.storage.create('port_5858', data)
            else:
                data = {'connCount': connections, 'queryTime': querytime}
                self.storage.create('port_5858', data)
            finally:
                gevent.sleep(60)

    def run(self):
        gevent.spawn(self.storageTask).join()


if __name__ == '__main__':
    app = StorageTask(config)
    logger.info('start 5858 port connections storage task ...')
    while True:
        app.run()
        gevent.sleep(3)