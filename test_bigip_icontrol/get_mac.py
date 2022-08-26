[root@ci-6987813-rdo-qzhao ~]# cat get_mac.py
# -*- coding: utf-8 -*-

from f5_openstack_agent.lbaasv2.drivers.bigip.resource_helper import \
    BigIPResourceHelper
from f5_openstack_agent.lbaasv2.drivers.bigip.resource_helper import \
    ResourceType
from f5.bigip import ManagementRoot

partition="Project_6fd06a50b7824ae48386565786e94b38"
name="vlan-143"
bigip = ManagementRoot(
    "10.145.64.180",
    "admin",
    "admin@f5.com",
    timeout=10,
    debug=True
)
vlan_manager = BigIPResourceHelper(ResourceType.vlan)
import pdb; pdb.set_trace()
stat_keys = ['macTrue']
result = vlan_manager.get_stats(
    bigip, name=name, partition=partition, stat_keys=stat_keys)
# result = result.stats.load()
# result.attrs['selfLink']
print result.entries['https://localhost/mgmt/tm/net/vlan/~Project_6fd06a50b7824ae48386565786e94b38~vlan-143/stats']['nestedStats']['entries']['macTrue']['description']
