# -*- coding: utf-8 -*-

from f5_openstack_agent.lbaasv2.drivers.bigip.resource_helper import \
    BigIPResourceHelper
from f5_openstack_agent.lbaasv2.drivers.bigip.resource_helper import \
    ResourceType
from f5.bigip import ManagementRoot

bigip = ManagementRoot(
    # "10.250.2.211",
    # "admin",
    # "P@ssw0rd123",
    "10.145.73.139",
    "admin",
    "admin@f5.com",
    timeout=10,
    debug=True
)
route_manager = BigIPResourceHelper(ResourceType.route)
member_manager = BigIPResourceHelper(ResourceType.member)
# route_manager.load(bigip, name="xxx", partition="Common")
result = route_manager.get_resources(bigip, partition="Common")
print result

result = member_manager.get_resources(bigip, partition="Common")
print result

# model={
    # "name":"xxxx",
    # "partition": "Common",
    # "network":"10.250.34.0%56/24"
    # "pool":"/Common/Default_GW_Pool"
# }
# result = route_manager.create(bigip, model)
# print result


