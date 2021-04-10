# -*- coding: utf-8 -*-

import sys
from oslo_config import cfg
from neutron.common import config as common_config
import f5_openstack_agent.lbaasv2.drivers.bigip.agent_manager as manager
from f5_openstack_agent.lbaasv2.drivers.bigip import constants_v2
from f5_openstack_agent.lbaasv2.drivers.bigip import icontrol_driver
from f5_openstack_agent.lbaasv2.drivers.bigip import resync_icontrol
from f5_openstack_agent.lbaasv2.drivers.bigip import plugin_rpc
try:
    from neutron_lib import context as ncontext
except ImportError:
    from neutron import context as ncontext

import oslo_messaging
import time
from f5_openstack_agent.lbaasv2.drivers.bigip.resync.db import queries

conf = cfg.CONF

import pdb; pdb.set_trace()

conf.register_opts(manager.OPTS)
conf.register_opts(icontrol_driver.OPTS)

conf(sys.argv[1:])
# conf(default_config_files=['/etc/neutron/neutron.conf', '/etc/neutron/services/f5/f5-openstack-agent.ini'])
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
    db_rpcclient = set_up_db_rpcclient()
    db_query = queries.Queries()
    demo_lb_id = "71ed67ad-fea0-427f-8b29-88db808db186"
    lb = db_query.get_loadbalancer(demo_lb_id)
    import pdb; pdb.set_trace()
    print lb
    # admin_lb_id = "b2d6bdc3-d08c-48d9-8676-a39229e7148d"
    admin_lb_id = "b2d6bdc3-d08c-48d9-8676-a39229e7148d"
    lb = db_query.get_loadbalancer(admin_lb_id)
    print lb
    # miss_lb_id = "36a7aa8f-dc5f-4d95-89a6-2b3ff4de33d3"
    # svc = db_rpcclient.get_service_by_loadbalancer_id(
        # admin_lb_id)
    # # svc = db_rpcclient.get_service_by_loadbalancer_id(
    # #     miss_lb_id)
    # icontrol = resync_icontrol.ResynciControlDriver(conf, db_rpcclient)
    # icontrol.connect()
    # icontrol.service_exists(svc)
# =======
    # t1 = time.time()
    # db_rpcclient = set_up_db_rpcclient()
    # lb_id = "1ca0d78c-2d05-48c9-9eed-4c803754603e"
    # svc = db_rpcclient.get_service_by_loadbalancer_id(
        # lb_id)
    # icontrol = resync_icontrol.ResynciControlDriver(conf, db_rpcclient)
    # icontrol.connect()
    # icontrol.service_exists(svc)
    # t2 = time.time()
    # print(t2-t1)
# >>>>>>> 9b01f027326339b90f1a37138b31d97ebcea69c8
