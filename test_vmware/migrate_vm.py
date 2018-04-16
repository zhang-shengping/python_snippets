#!/usr/bin/env python
# encoding: utf-8

from oslo_vmware import api
from nova.virt.vmwareapi import driver
from oslo_vmware import vim_util
from nova.virt.vmwareapi import vm_util
import copy

import pdb

# session = api.VMwareAPISession(
#     '172.18.211.201',
#     'administrator@os.com',
#     'Naguan.123',
#     10,
#     0.1
# )

session = driver.VMwareAPISession(
    host_ip='172.18.211.201',
    host_port=443,
    username='administrator@os.com',
    password='Naguan.123',
    retry_count=10,
    scheme="https",
    cacert=None,
    insecure=True
)

client_factory = session.vim.client.factory
# target = client_factory.create('ns0:HostSystem')
# ----------------------------------------------------------------------------------------
#   migrate vm
# ----------------------------------------------------------------------------------------
vm_ref = vm_util.get_vm_ref_from_name(session, 'shengping-test')
host_refa = session._call_method(vim_util, "get_object_property", vm_ref, "runtime.host")
target = copy.deepcopy(host_refa)
target.value='host-13'
pdb.set_trace()
pr = client_factory.create('ns0:VirtualMachineMovePriority')
pr = pr.defaultPriority
result = session._call_method(session.vim, "MigrateVM_Task", vm_ref, host=target, priority=pr)
# result = session._call_method(session, "MigrateVM_Task", vm_ref, host=target)
# host_refb = vm_util.get_host_ref(session)
# ----------------------------------------------------------------------------------------
