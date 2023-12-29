# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-12 20:30:30
LastEditTime: 2023-12-23 18:07:25
Description: xxx
'''

from abc import ABCMeta, abstractmethod
import logging
import socket
from gevent.queue import Queue
from logger import logger

from geventwebsocket.websocket import WebSocket
from geventwebsocket.handler import WebSocketHandler
import typing

from network import tcp_server
from network import ws_server


class net_stream(metaclass=ABCMeta):
    
    @abstractmethod
    def writeMsg(self, data:bytes):
        pass
    
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def writePump(self):
        pass

    @abstractmethod
    def readPump(self):
        pass

class socket_steam(net_stream):

    def __init__(self, socket:socket.socket, addr:tuple, net_server:"tcp_server.tcp_server", max_msg_queue_size=10000):
        self.socket = socket
        self._wirter_buff = Queue(max_msg_queue_size)
        self.connect_id = socket.fileno()
        self.sockname = addr
        self.closed = False
        self.net_server = net_server

    @classmethod
    def debug(cls, msg:str):
        logger.debug("[{}] {}".format(cls.__name__, msg))


    def writeMsg(self, data:bytes):
        return self._wirter_buff.put(data)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.socket.close()
        socket_steam.debug("closed, addr {} connect_id {}".format(self.sockname, self.connect_id))

    def writePump(self):
        try:
            socket_steam.debug("start writePump, connect_id {}".format(self.connect_id))
            while not self.closed:
                data:bytes = self._wirter_buff.get()
                length = len(data)
                prefix:bytes = length.to_bytes(length=2, byteorder="big")
                self.socket.send(prefix + data)
                socket_steam.debug("send msg {} len {}".format(data, length))
        except Exception as e:
            socket_steam.debug("error send from {} exception {}".format(self.sockname, e))
        finally:
            self.net_server.close_client(self.connect_id)

    

    def readPump(self):
        try:
            socket_steam.debug("start readPump, connect_id {}".format(self.connect_id))
            while not self.closed:
                prefix = self.socket.recv(2)
                if not prefix:
                    socket_steam.debug("no prefix")
                    break
                length = int.from_bytes(prefix, byteorder="big")
                data = self.socket.recv(length)
                if not data:
                    socket_steam.debug("no data")
                    break
                self.net_server.pushReadMsg(self.connect_id, data)
                socket_steam.debug("read msg {} len {}".format(data, length))
        except Exception as e:
            socket_steam.debug("error read from {} exception {}".format(self.sockname, e))
        finally:
            self.net_server.close_client(self.connect_id)


class ws_stream(net_stream):

    def __init__(self, ws:WebSocket, connect_id, server:ws_server.ws_server, max_msg_queue_size=10000) -> None:
        self.ws = ws
        self._wirter_buff = Queue(max_msg_queue_size)
        self.connect_id = connect_id
        self.sockname = ws.handler.client_address
        self.closed = False
        self.net_server = server

    @classmethod
    def debug(cls, msg:str):
        logger.debug("[{}] {}".format(cls.__name__, msg))

    def writeMsg(self, data:bytes):
        return self._wirter_buff.put(data)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.ws.close()
        ws_stream.debug("closed, addr {} connect_id {}".format(self.sockname, self.connect_id))

    def writePump(self):
        try:
            ws_stream.debug("start writePump, connect_id {}".format(self.connect_id))
            while not self.closed:
                data:bytes = self._wirter_buff.get()
                self.ws.send(data)
                ws_stream.debug("send msg {}".format(data))
        except Exception as e:
            ws_stream.debug("error send from {} exception {}".format(self.sockname, e))
        finally:
            self.net_server.close_client(self.connect_id)

    def readPump(self):
        try:
            ws_stream.debug("start readPump, connect_id {}".format(self.connect_id))
            while not self.closed:
                data = self.ws.receive()
                if data is None:
                    break
                self.net_server.pushReadMsg(self.connect_id, data)
                ws_stream.debug("read msg {}".format(data))
        except Exception as e:
            ws_stream.debug("error read from {} exception {}".format(self.sockname, e))
        finally:
            self.net_server.close_client(self.connect_id)