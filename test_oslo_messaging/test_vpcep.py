#!/usr/bin/env python
# encoding: utf-8


# NOTE:We are using eventlet executor and
# time.sleep(1), therefore, the server code needs to be
# monkey-patched.
import eventlet
eventlet.monkey_patch()

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging
import time
import f5_endpoint_agent.endpoint.drivers.bigip.agent_manager as manager
from oslo_messaging.rpc import dispatcher

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
# CONF(default_config_files=['test.conf','/etc/neutron/neutron.conf'])
CONF(default_config_files=['/etc/neutron/neutron.conf', '/etc/neutron/services/f5/f5-endpoint-agent.ini'])

class TestEndpoint(object):

    def create_vpcep(self, ctx, payload):
        print payload
        return "ok"

transport = oslo_messaging.get_rpc_transport(cfg.CONF)

target = oslo_messaging.Target(topic='f5-endpoint-process-on-agent_VPCEP',
                               server='neutron-server-1.pdsea.f5net.com')
endpoints = [
    # TestEndpoint()
    manager.EndpointAgentManager(cfg.CONF)
]
access_policy = dispatcher.DefaultRPCAccessPolicy
server = oslo_messaging.get_rpc_server(transport, target, endpoints,
                                       access_policy = access_policy,
                                       executor='eventlet')
try:
    # LOG.info("Oslo Logging")
    server.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server")

server.stop()
server.wait()
