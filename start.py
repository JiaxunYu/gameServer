# -*- coding: utf-8 -*-
'''
Author: yujiaxun
Date: 2023-12-26 20:26:46
LastEditTime: 2023-12-26 20:27:47
Description: xxx
'''

from gevent import monkey
monkey.patch_all()
import os
from network import gate

if __name__ == "__main__":
	
    os.environ['GEVENT_SUPPORT']= "True"
    gate = gate.Gate("./config/config.json")
    gate.start()