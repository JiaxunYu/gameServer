# -*- coding: utf-8 -*-Logger
'''
Author: yujiaxun
Date: 2023-12-13 22:42:06
LastEditTime: 2023-12-25 13:27:46
Description: xxx
'''

import logging


class Logger:
    def __init__(self, name="", level=logging.DEBUG):
        self.logger = logging.getLogger("default" if name == "" else name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s')

        if name == "":
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            file_handler = logging.FileHandler("./log/{}.log".format(name))
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def setLevel(self, level: int):
        self.logger.setLevel(level)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


g_file_2_log = {}
g_log_level = logging.DEBUG


def info(msg: str, file_name: str = "", level=logging.DEBUG):
    if g_file_2_log.get(file_name, None) is None:
        g_file_2_log[file_name] = Logger(file_name, level)
    logger: Logger = g_file_2_log[file_name]
    logger.logger.info(msg)


def error(msg: str, file_name: str = "", level=logging.DEBUG):
    if g_file_2_log.get(file_name, None) is None:
        g_file_2_log[file_name] = Logger(file_name, level)
    logger: Logger = g_file_2_log[file_name]
    logger.error(msg)


def debug(msg: str, file_name: str = "", level=logging.DEBUG):
    if g_file_2_log.get(file_name, None) is None:
        g_file_2_log[file_name] = Logger(file_name, level)
    logger: Logger = g_file_2_log[file_name]
    logger.debug(msg)

def get_logger(file_name: str) -> Logger:
    return g_file_2_log.get(file_name, None)


def test():
    # 创建一个logger
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler("./log/{}.log".format("mylogger"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 输出日志
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')
    print(logger.handlers)


if __name__ == "__main__":
    debug('This is a debug message')
    info('This is an info message')
    # logger = get_logger("")
    # logger.setLevel(logging.INFO)
    debug('This is a debug message')
    info('This is an info message111', "mylogger")
    # test()
    # log.warning('This is a warning message')
    # error('This is an error message')
    # log.critical('This is a critical message')
