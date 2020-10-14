#!/usr/bin/env python
# encoding: utf-8

import eventlet
eventlet.monkey_patch()

from oslo_config import cfg
import oslo_messaging as messaging
import time

CONF = cfg.CONF
CONF(default_config_files=['test.conf'])

# class TestClient(object):
# 
#     def __init__(self, transport):
#         target = messaging.Target(topic='test', version='2.0')
#         self._client = messaging.RPCClient(transport, target)
#     def test(self, ctxt, arg):
#         cctxt = self._client.prepare(version='2.5')
#         return cctxt.call({}, 'test', arg="hello")

ctxt = {}
arg = "hello there"
transport = messaging.get_rpc_transport(cfg.CONF)
# target = messaging.Target(topic='test', version='2.0')
# target = messaging.Target(topic='test')
target = messaging.Target(topic='aaaaaaa')
client = messaging.RPCClient(transport, target)
t = client.call(ctxt, 'test', arg=arg)
print t
