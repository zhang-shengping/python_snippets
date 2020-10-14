#!/usr/bin/env python
# encoding: utf-8

from oslo_config import cfg
import oslo_messaging as om

CONF = cfg.CONF

CONF(default_config_files=['test.conf'])

transport = om.get_transport(cfg.CONF)

target = om.Target(topic='testme', server='10.145.72.51')

class TestEndpoint(object):
  def test_method1(self, ctx, arg):
    res = "Result from test_method1 " + str(arg) 
    print res
    return res

  def test_method2(self, ctx, arg):
    res = "Result from test_method2 " + str(arg) 
    print res
    return res

endpoints = [TestEndpoint()]

server = om.get_rpc_server(transport, target, endpoints, executor='blocking')

server.start()
