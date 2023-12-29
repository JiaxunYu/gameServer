# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-21 12:55:03
LastEditTime: 2023-12-26 20:39:50
Description: xxx
'''

import importlib
import json
import typing
from network import parser
from conf import rpcConf
from logger import logger
from utils import utils

if typing.TYPE_CHECKING:
    pass



class RpcRacket:
    '''
    rpc消息体
    '''

    def __init__(self, parser:parser.Parser):
        self._receiver: str = None
        self._method: str = None
        self._args: list = None
        self._data_in_str = None  # type: str
        self.client = None
        self.parser = parser

    def assign(self, receiver, method, args=None):
        self._method = method
        self._receiver = receiver
        self._args = args

    @property
    def receiver(self):
        return self._receiver

    @property
    def method(self):
        return self._method

    @property
    def args(self):
        return self._args

    def toBytes(self) -> bytes:
        data = {}
        data[rpcConf.receiver] = self._receiver
        data[rpcConf.method] = self._method
        data[rpcConf.args] = self._args
        self.parser.dumps(data)

    def loadBytes(self, raw_data):
        data = self.parser.loads(raw_data)
        print(data)
        self._receiver = data[rpcConf.receiver]
        self._method = data[rpcConf.method]
        self._args = data[rpcConf.args]

    def __str__(self) -> str:
        if self._data_in_str:
            return self._data_in_str
        data = {}
        data[rpcConf.receiver] = self._receiver
        data[rpcConf.method] = self._method
        data[rpcConf.args] = self._args
        self._data_in_str = str(json.dumps(data))
        return self._data_in_str
    

class RpcDispatcher:
    '''
    rpc分发
    rpc_receivers的value可以是module，类或者类实例
    '''
    def __init__(self):
        self.rpc_receivers: dict[str, typing.Any] = {}

    def register(self, name:str, receiver:typing.Any):
        self.rpc_receivers[name] = receiver

    def unregister(self, name:str):
        if name in self.rpc_receivers:
            self.rpc_receivers.pop(name)
    
    @classmethod
    def debug(cls, msg:str):
        logger.debug("[{}] {}".format(cls.__name__, msg))

    @classmethod
    def info(cls, msg:str):
        cls.debug(msg)
        logger.info(msg, "rpc")

    
    def handleRpc(self, connect_id:int, row_data:bytes):
        rpcPkg = RpcRacket(parser.msgpackParser)
        rpcPkg.loadBytes(row_data)
        #如果是客户端协议，需要读取协议编号已经进行协议参数校验
        receiver_anme = rpcPkg.receiver
        method_name = rpcPkg.method
        args = rpcPkg.args
        if args is None:
            args = []
        args = [connect_id] + args
        receiver = self.rpc_receivers.get(receiver_anme, None)
        RpcDispatcher.debug("handleRpc, connect_id {} rpcPkg {}".format(connect_id, rpcPkg))
        if receiver is None:
            try:
                receiver = importlib.import_module(receiver_anme)
            except Exception as e:
                RpcDispatcher.info("has no receiver: {}".format(receiver_anme))
                return False
        func = getattr(receiver, method_name, None)
        if not callable(func):
            RpcDispatcher.info("{}.{} is not callable".format(receiver_anme, method_name))
            return False
        try:
            func(*args)
            return True
        except Exception as e:
            RpcDispatcher.info("handleRpc err {}".format(e))
            return False


rpcDispatcher = RpcDispatcher()

if __name__ == "__main__":
    print(utils.is_module("test.test_hello"))
    receiver = importlib.import_module("test.test_hello")
    print(receiver)
    func = getattr(receiver, "test_hello", None)
    print(func)
    print(func())