# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-11 20:22:35
LastEditTime: 2023-12-25 13:35:21
Description: base net server
'''

from abc import abstractmethod, ABCMeta
from logger import logger
from gevent.queue import Queue
import gevent.queue

class base_server(metaclass=ABCMeta):

    def __init__(self) -> None:
        self.closed = False
        self._read_buff:Queue = None
        pass

    @classmethod
    def debug(cls, msg:str):
        logger.debug("[{}] {}".format(cls.__name__, msg))

    @classmethod
    def info(cls, msg:str):
        cls.debug(msg)
        logger.info(msg, cls.__name__)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def readMsg(self, timeout=None) -> tuple:
        if self.closed and self._read_buff.empty():
            return None
        try:
            msg = self._read_buff.get(timeout=timeout)
            self.__class__.debug("read msg {}".format(msg))
        except gevent.queue.Empty:
            return None
        except Exception as e:
            self.__class__.info("read Msg error: {}".format(e))
            return None
        return msg

if __name__ == "__main__":
    server = base_server()