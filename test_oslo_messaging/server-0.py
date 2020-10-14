#!/usr/bin/env python
# encoding: utf-8

import eventlet
eventlet.monkey_patch()

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
import time

LOG = logging.getLogger(__name__) 

CONF = cfg.CONF
CONF(default_config_files=['test.conf'])

class ServerControlEndpoint(object):

    # target = oslo_messaging.Target(namespace='control',
    #                                version='2.0')
    target = oslo_messaging.Target(namespace='pzhang-0')

    def __init__(self, server):
        self.server = server

    def stop(self, ctx):
        if self.server:
            self.server.stop()

class TestEndpoint(object):

    def test(self, ctx, arg):
        print "incoming-0"
        return arg

transport = oslo_messaging.get_rpc_transport(cfg.CONF)

target = oslo_messaging.Target(topic='aaaaaaa', server='server-0')
endpoints = [
    ServerControlEndpoint(None),
    TestEndpoint(),
]
server = oslo_messaging.get_rpc_server(transport, target, endpoints,
                                       executor='eventlet')
try:
    LOG.info("Oslo Logging")
    server.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server")

server.stop()
server.wait()
