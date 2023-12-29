# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-11 20:39:47
LastEditTime: 2023-12-26 20:49:20
Description: tcp_server
'''
import copy
import gevent
import socket
from network.base_server import base_server
import random
from logger import logger
from gevent.queue import Queue
from gevent import queue
from network import net_stream


class tcp_server(base_server):

    def __init__(self, port, max_msg_queue_size = 10000, listen_num=1000) -> None:
        super(tcp_server, self).__init__()
        self.socket:socket.socket = None
        self.port = port
        self.listen_num = listen_num
        self.closed = False
        self.max_msg_queue_size = max_msg_queue_size
        self.clients = {}
        self._read_buff = Queue(max_msg_queue_size)
        self.coroutines: list[gevent.Greenlet] = []

    def pushReadMsg(self, connect_id:int, data:bytes):
        self._read_buff.put((connect_id, data))
        tcp_server.debug("push msg {}".format(data))

    def writeMsg(self, connect_id:int, data:bytes) -> bool:
        client:net_stream.socket_steam = self.clients.get(connect_id, None)
        if client:
            tcp_server.debug("writeMsg to {}".format(connect_id))
            client.writeMsg(data)
            return True
        return False
    
    def stop(self):
        if self.closed:
            return
        self.closed = True
        connect_list = list(self.clients.keys())
        for connect_id in connect_list:
            self.close_client(connect_id)
        self.socket.close()

    def close_client(self, connect_id:int):
        client:net_stream.socket_steam = self.clients.get(connect_id, None)
        if client:
            self.clients.pop(connect_id)
            client.close()
            tcp_server.info("close client, addr {} connect_id {}".format(client.sockname, connect_id))

    def new_connection(self, client_socket:socket.socket, address:tuple):
        connect_id = client_socket.fileno()
        client = net_stream.socket_steam(client_socket, address, self, self.max_msg_queue_size)
        self.clients[connect_id] = client
        tcp_server.info("new_connection, addr {} connect_id {}".format(address, connect_id))
        read_coroutine = gevent.spawn(client.readPump)
        write_coroutine = gevent.spawn(client.writePump)
        self.coroutines.append(read_coroutine)
        self.coroutines.append(write_coroutine)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), self.port))
        tcp_server.info("start server, addr {}".format(self.socket.getsockname()))
        self.socket.listen(self.listen_num)
        while not self.closed:
            try:
                client_socket, address = self.socket.accept()
                self.new_connection(client_socket, address)
            except Exception as e:
                tcp_server.info("error in accept {}".format(e))
        gevent.joinall(self.coroutines)
        tcp_server.info("server stop")

def deal_msg(server:tcp_server, connect_id:int, data:bytes):
        deal_time = random.randint(0, 3)
        logger.info("{} deal msg time: {}".format(connect_id, deal_time))
        gevent.sleep(deal_time)
        server.writeMsg(connect_id, data)
        gevent.sleep(1)

def process(server:tcp_server):
    while not server.closed:
        msg = server.readMsg(timeout=2)
        if msg is None:
            continue
        connect_id, data = msg
        gevent.spawn(deal_msg, server, connect_id, data)

def test_server():
    server = tcp_server(8888, 1000, 1000)
    coroutine_list = []
    coroutine_list.append(gevent.spawn(server.start))
    coroutine_list.append(gevent.spawn(process, server))
    gevent.joinall(coroutine_list)

if __name__ == "__main__":
    test_server()