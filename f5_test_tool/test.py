# -*- coding: utf-8 -*-

import sys
from oslo_config import cfg
from oslo_db import options as db_options
from neutron_lib import context as ncontext
from neutron_lbaas.db.loadbalancer import loadbalancer_dbv2 as ldbv2

# import pdb; pdb.set_trace()
# connection = mysql+pymysql://root:stackdb@127.0.0.1/neutron?charset=utf8
db_options.set_defaults(cfg.CONF)
cfg.CONF(sys.argv[1:])

context = ncontext.get_admin_context()
db = ldbv2.LoadBalancerPluginDbv2()
provider_name = db.get_provider_names_used_in_loadbalancers(context)
print provider_name
