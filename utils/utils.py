# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-25 19:27:56
LastEditTime: 2023-12-25 19:28:20
Description: xxx
'''

import importlib

def is_module(name):
    loader = importlib.find_loader(name)
    return loader is not None