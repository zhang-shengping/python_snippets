# -*- coding: utf-8 -*-

import sys
from oslo_config import cfg
from oslo_db import options as db_options
from neutron_lib import context as ncontext
from neutron_lbaas.db.loadbalancer import loadbalancer_dbv2 as ldbv2

try:
    from neutron.common import config as common_config
    from neutron.common import rpc as n_rpc
    try:
        from neutron.conf.agent import common as config
    except Exception:
        from neutron.agent.common import config
    # for openstack backward compatible
    try:
        # q version
        from neutron.conf.agent.common import INTERFACE_OPTS
    except Exception:
        # m/n/o/p version
        from neutron.agent.linux.interface import OPTS as INTERFACE_OPTS
except ImportError as Error:
    pass

import f5_openstack_agent.lbaasv2.drivers.bigip.agent_manager as manager

from oslo_utils import importutils

# import pdb; pdb.set_trace()
# connection = mysql+pymysql://root:stackdb@127.0.0.1/neutron?charset=utf8
db_options.set_defaults(cfg.CONF)

cfg.CONF.register_opts(manager.OPTS)
cfg.CONF.register_opts(INTERFACE_OPTS)
config.register_agent_state_opts_helper(cfg.CONF)
config.register_root_helper(cfg.CONF)

common_config.init(sys.argv[1:])
cfg.CONF(sys.argv[1:])

config.setup_logging()

context = ncontext.get_admin_context()
db = ldbv2.LoadBalancerPluginDbv2()
loadbalancer_id = "4c7b2839-798f-479f-8893-a9f2e51e723f"

def load_driver(conf):
    lbdriver = None
    try:
        lbdriver = importutils.import_object(
            conf.f5_bigip_lbaas_device_driver,
            conf)
        return lbdriver
    except ImportError as ie:
        raise SystemExit(msg)

with context.session.begin(subtransactions=True):
    lb = db.get_loadbalancer(context, id=loadbalancer_id)
    print lb.__dict__

# we need to build service here

import pdb; pdb.set_trace()
driver = load_driver(cfg.CONF)
driver.service_exists([])
