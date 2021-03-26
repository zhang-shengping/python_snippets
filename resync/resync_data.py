# -*- coding: utf-8 -*-

import sys
from oslo_config import cfg
from neutron.common import config as common_config
import f5_openstack_agent.lbaasv2.drivers.bigip.agent_manager as manager
from f5_openstack_agent.lbaasv2.drivers.bigip import constants_v2
from f5_openstack_agent.lbaasv2.drivers.bigip import resync_icontrol
from f5_openstack_agent.lbaasv2.drivers.bigip import plugin_rpc
try:
    from neutron_lib import context as ncontext
except ImportError:
    from neutron import context as ncontext

import oslo_messaging
import time

conf = cfg.CONF

conf.register_opts(manager.OPTS)
conf(default_config_files=['/etc/neutron/neutron.conf', '/etc/neutron/services/f5/f5-openstack-agent.ini'])
common_config.init(sys.argv[1:])

context = ncontext.get_admin_context_without_session()

RPC_API_VERSION = '1.0'
target = oslo_messaging.Target(version='1.0')
transport = oslo_messaging.get_rpc_transport(conf)

if conf.agent_id:
    agent_host = conf.agent_id

def set_up_db_rpcclient():
    topic = constants_v2.TOPIC_PROCESS_ON_HOST_V2
    if conf.environment_specific_plugin:
        topic = topic + '_' + conf.environment_prefix

    db_rpc = plugin_rpc.LBaaSv2PluginRPC(
        topic,
        context,
        conf.environment_prefix,
        conf.environment_group_number,
        agent_host
    )

    return db_rpc

if __name__ == "__main__":
    t1 = time.time()
    db_rpcclient = set_up_db_rpcclient()
    lb_id = "1ca0d78c-2d05-48c9-9eed-4c803754603e"
    svc = db_rpcclient.get_service_by_loadbalancer_id(
        lb_id)
    icontrol = resync_icontrol.ResynciControlDriver(conf, db_rpcclient)
    icontrol.connect()
    icontrol.service_exists(svc)
    t2 = time.time()
    print(t2-t1)
