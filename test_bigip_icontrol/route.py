# -*- coding: utf-8 -*-

from f5_openstack_agent.lbaasv2.drivers.bigip.resource_helper import \
    BigIPResourceHelper
from f5_openstack_agent.lbaasv2.drivers.bigip.resource_helper import \
    ResourceType
from f5.bigip import ManagementRoot

bigip = ManagementRoot(
    "10.250.2.211",
    "admin",
    "P@ssw0rd123"
    timeout=10,
    debug=True
)
self.route_manager = BigIPResourceHelper(ResourceType.route)

self.route_manager.get
