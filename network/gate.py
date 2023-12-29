# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-17 21:06:32
LastEditTime: 2023-12-25 22:03:39
Description: xxx
'''

# Python使用gevent封装WebSocket、TCP和HTTP服务

import os
os.environ['GEVENT_SUPPORT']= "True"
import gevent
from gevent import monkey
monkey.patch_all()

from network import tcp_server, base_server, ws_server
from network import rpc
from logger import logger
import json
import signal

class Gate:
    def __init__(self, config_file):
        self.config:dict = self.load_config(config_file)
        self.servers:list[base_server.base_server] = []
        self.closed = False

    def load_config(self, config_file):
        with open(config_file, "r") as f:
            return json.load(f)
        
    @classmethod
    def info(cls, msg:str):
        logger.info(msg, "gate")

    def start(self):
        coroutine_list = []
        tcp_config = self.config.get("tcp", None)
        ws_config = self.config.get("ws", None)
        if isinstance(tcp_config, dict):
            # 启动TCP服务器
            Gate.info("start tcp server, config {}".format(tcp_config))
            port = tcp_config.get("port", 8888)
            max_msg_queue_size = tcp_config.get("msg_quene_size", 1000)
            listen_num = tcp_config.get("max_listen_num", 1000)
            server = tcp_server.tcp_server(port=port, max_msg_queue_size=max_msg_queue_size, listen_num=listen_num)
            coroutine_list.append(gevent.spawn(server.start))
            self.servers.append(server)
            coroutine_list.append(gevent.spawn(self.process, server))
        if isinstance(ws_config, dict):
            #启动webscoket服务器
            Gate.info("start tcp server, config {}".format(ws_config))
            port = ws_config.get("port", 8887)
            max_msg_queue_size = tcp_config.get("msg_quene_size", 1000)
            server = ws_server.ws_server(port, max_msg_queue_size)
            coroutine_list.append(gevent.spawn(server.start))
            self.servers.append(server)
            coroutine_list.append(gevent.spawn(self.process, server))
        # 监听kill信号
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        # 运行主循环
        gevent.joinall(coroutine_list)
        Gate.info("gate stop gracefully")

    def process(self, server: base_server.base_server):
        is_empty = False
        #is_empty用来保证所有的消息都被处理完
        while not self.closed or not is_empty:
            Gate.info("start process msg")
            msg = server.readMsg(timeout=1)
            if msg is None:
                is_empty = True
                continue
            is_empty = False
            connect_id, row_data = msg
            rpc.rpcDispatcher.handleRpc(connect_id, row_data)

    # 处理kill信号
    def handle_signal(self, signum, frame):
        self.closed = True
        Gate.info("Received signal {}, exiting...".format(signum))
        for server in self.servers:
            server.stop()


if __name__ == "__main__":
    print(os.environ.get('GEVENT_SUPPORT'))
    gate = Gate("./config/config.json")
    gate.start()
