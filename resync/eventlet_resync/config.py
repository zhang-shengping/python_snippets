# -*- coding: utf-8 -*-

from oslo_config import cfg
import sys

import f5_openstack_agent.lbaasv2.drivers.bigip.agent_manager as manager
from f5_openstack_agent.lbaasv2.drivers.bigip import icontrol_driver
from oslo_db import options

# We calll this in order to init n_rpc.init(cfg.CONF)
# from neutron.common import config as common_config
# common_config.init(parse_args.conf_files)

tool_opts = [
    cfg.IntOpt("f5_check_thread",
               default=1,
               help=_("Green Threads"))
]

def regist_cli_opts(conf=cfg.CONF):
    conf.register_cli_opts(tool_opts)

def load_options(args=sys.argv[1:], conf=cfg.CONF):
    # regist_cli_opts()
    conf.register_opts(manager.OPTS)
    conf.register_opts(icontrol_driver.OPTS)
    options.set_defaults(conf)
    conf(args, project="f5-resync-tool" )


if __name__ == "__main__":
    load_options()
    conf = cfg.CONF
    print conf.f5_check_thread
    print conf.database.connection
