# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-21 19:24:44
LastEditTime: 2023-12-25 22:54:07
Description: xxx
'''

import json
from abc import abstractmethod, ABCMeta
import msgpack
from typing import Any


class Parser(metaclass=ABCMeta):
    '''
    用于序列化的解析器抽象基类
    '''

    @abstractmethod
    def loads(self, raw_data: bytes) -> Any:
        pass

    @abstractmethod
    def dumps(self, data: dict):
        pass


class JsonParser(Parser):

    def loads(self, raw_data: bytes) -> Any:
        return json.loads(raw_data)

    def dumps(self, data: Any) -> bytes:
        return bytes(json.dumps(data), "utf-8")


class MsgPackParser(Parser):

    def loads(self, raw_data: bytes) -> Any:
        return msgpack.loads(raw_data, encoding='utf-8')

    def dumps(self, data: Any) -> bytes:
        return msgpack.dumps(data)

msgpackParser = MsgPackParser()
sonParser = JsonParser()

if __name__ == "__main__":
    parser = MsgPackParser()
    data = parser.dumps({1: 2})
    print(type(data))
    print(data)
