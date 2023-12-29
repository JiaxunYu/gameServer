# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-17 21:28:22
LastEditTime: 2023-12-23 18:59:29
Description: xxx
'''


import socket
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from geventwebsocket.websocket import WebSocketError
from network.base_server import base_server
from gevent.queue import Queue
import gevent
import gevent.queue
from geventwebsocket.websocket import WebSocket
from logger import logger
from network import net_stream
import random


class ws_server(base_server):
    
    def __init__(self, port:int, max_msg_queue_size = 10000) -> None:
        print(port)
        super(ws_server, self).__init__()
        self.clients = {}
        self._read_buff = Queue(max_msg_queue_size)
        self.coroutines: list[gevent.Greenlet] = []
        self.server:WSGIServer = None
        self.port = port
        self.max_msg_queue_size = max_msg_queue_size
        self.closed = False
        self._cur_connect_id = 0

    # def readMsg(self, timeout=None) -> tuple:
    #     if self.closed:
    #         return None
    #     try:
    #         msg = self._read_buff.get(timeout=timeout)
    #         # tcp_server.debug("read msg {}".format(msg))
    #     except gevent.queue.Empty:
    #         return None
    #     return msg

    def pushReadMsg(self, connect_id:int, data:bytes):
        self._read_buff.put((connect_id, data))

    def writeMsg(self, connect_id:int, data:bytes) -> bool:
        client:net_stream.ws_stream = self.clients.get(connect_id, None)
        if client:
            ws_server.info("writeMsg to {}".format(connect_id))
            client.writeMsg(data)
            return True
        return False

    def stop(self):
        self.closed = True
        for connect_id in self.clients.keys():
            self.close_client(connect_id)
        self.server.stop()
        # tcp_server.info("server stop")

    def close_client(self, connect_id:int):
        client:net_stream.ws_stream = self.clients.get(connect_id, None)
        if client:
            self.clients.pop(connect_id)
            client.close()
            ws_server.info("close client, addr {} fileno {}".format(client.sockname, connect_id))

    def handle_request(self, environ, start_response):
        if environ["PATH_INFO"] == "/websocket":
            ws:WebSocket = environ["wsgi.websocket"]
            connect_id = self.new_connection(ws)
            client:net_stream.ws_stream = self.clients[connect_id]
            read_coroutine = gevent.spawn(client.readPump)
            write_coroutine = gevent.spawn(client.writePump)
            self.coroutines.append(read_coroutine)
            self.coroutines.append(write_coroutine)
            gevent.joinall([read_coroutine, write_coroutine])
        else:
            start_response("404 Not Found", [])
        return []

    def gen_connect_id(self):
        self._cur_connect_id += 1
        return self._cur_connect_id

    def new_connection(self, ws:WebSocket):
        connect_id = self.gen_connect_id()
        client = net_stream.ws_stream(ws, connect_id, self, self.max_msg_queue_size)
        self.clients[connect_id] = client
        ws_server.info("new_connection, addr {} connect_id {}".format(client.sockname, connect_id))
        return connect_id

    def start(self):
        self.server = WSGIServer((socket.gethostname(), self.port), self.handle_request, handler_class=WebSocketHandler)
        ws_server.info("start server, addr {}".format(self.server.address))
        self.coroutines.append(gevent.spawn(self.server.serve_forever))
        gevent.joinall(self.coroutines)
        ws_server.info("server stop")

def deal_msg(server:ws_server, connect_id:int, data:bytes):
        deal_time = random.randint(0, 3)
        logger.info("{} deal msg time: {}".format(connect_id, deal_time))
        gevent.sleep(deal_time)
        server.writeMsg(connect_id, data)
        gevent.sleep(1)

def process(server:ws_server):
    while not server.closed:
        connect_id, data = server.readMsg()
        gevent.spawn(deal_msg, server, connect_id, data)

def test_server():
    server = ws_server(8000, 1000)
    coroutine_list = []
    coroutine_list.append(gevent.spawn(server.start))
    coroutine_list.append(gevent.spawn(process, server))
    gevent.joinall(coroutine_list)

if __name__ == "__main__":
    test_server()