
import sys
from neutron.common import config as common_config
from oslo_config import cfg
from f5lbaasdriver.v2.bigip import agent_rpc
import oslo_messaging

try:
    from neutron_lib import context as ncontext
except ImportError:                                                                                                                                                  from neutron import context as ncontext


conf = cfg.CONF
conf(sys.argv[1:])
conf(default_config_files=['/etc/neutron/neutron.conf', '/etc/neutron/services/f5/f5-openstack-agent.ini'])
common_config.init(sys.argv[1:])

class FakeContext(object):
    def to_dict(self):
        return dict({"tenant_name": "test"})


class F5AgentEnv(object):
    def __init__(self, env='Project'):
        self.env = env


if __name__ == "__main__":
    f5agent = F5AgentEnv()
    rpcclient = agent_rpc.LBaaSv2AgentRPC(f5agent)

    # context = ncontext.get_admin_context_without_session()
    # rpcclient.create_loadbalancer(context, {}, {}, "resync_agent_id")
    
    fake_ctxt = FakeContext()
    rpcclient.create_loadbalancer(fake_ctxt, {}, {}, "resync_agent_id")

    # if context is {}, it wil have no to_dict() method,
    # then it report error in self.serializer.serialize_context(ctxt) method of 
    # /usr/lib/python2.7/site-packages/oslo_messaging/rpc/client.py +139
    # /opt/stack/neutron/neutron/common/rpc.py(252)serialize_context()
    # rpcclient.create_loadbalancer({}, {}, {}, "resync_agent_id")
