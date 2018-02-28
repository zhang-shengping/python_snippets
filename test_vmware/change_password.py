# from oslo_vmware import api
from nova.virt.vmwareapi import driver
from oslo_vmware import vim_util
from suds.client import Client
from nova.virt.vmwareapi import vm_util
import requests
import datetime
import mock


connection_info = mock.Mock() 

def prepare_instance():
    instance = mock.Mock()
    instance.uuid = 'e35a904f-fc08-4460-a119-4b7097f07658'
    instance.name = 'test-vm'
    return instance

# session = api.VMwareAPISession(
#     '172.28.8.247',      # vSphere host endpoint
#    'administrator@os.com', # vSphere username
#     'Vcenter123.',      # vSphere password
#     10,              # Number of retries for connection failures in tasks
#    0.1              # Poll interval for async tasks (in seconds)
# )

instance = prepare_instance()

session = driver.VMwareAPISession(
    host_ip='172.28.8.247',
    host_port=443,
    username='administrator@os.com',
    password='Vcenter123.',
    retry_count=10,
    scheme="https",
    cacert=None,
    insecure=True
)

client_factory = session.vim.client.factory

# vm_ref = vm_util.get_vm_ref(session, instance)
vm_ref = vm_util.get_vm_ref_from_name(session, 'test-vm')

# get manager object from content
content = session.vim.retrieve_service_content()
# manager object for guest operation
gopmgr = content.guestOperationsManager

# crate auth
# auth = client_factory.create('ns0:GuestAuthentication')
# managed object follows ploymorphism
auth = client_factory.create('ns0:NamePasswordAuthentication')
auth.interactiveSession = False
auth.username = 'root'
auth.password = 'Passw0rd'

# ---------------- create temp file for scirpt ---------------------#
# CreateTemporaryFileInGuest
filemgr = session._call_method(vim_util, 'get_object_property', gopmgr, 'fileManager')

# create file 
script = session._call_method(session.vim, "CreateTemporaryFileInGuest",
    filemgr, vm=vm_ref, auth=auth, prefix='change_', suffix='_password',
    directoryPath='/root')

# --------------- create temp file for output ---------------------#
output = session._call_method(session.vim, "CreateTemporaryFileInGuest",
    filemgr, vm=vm_ref, auth=auth, prefix='ps_', suffix='_output',
    directoryPath='/root')

#  -------------- init transfer file content ------------------- #
# InitiateFileTransferToGuest
attr = client_factory.create('ns0:GuestFileAttributes')
attr.accessTime = datetime.datetime.now()
attr.modificationTime = datetime.datetime.now()
attr.symlinkTarget = None

data = 'echo www.456 | passwd root --stdin >> ' + output

file_path = session._call_method(session.vim, "InitiateFileTransferToGuest",
    filemgr, vm=vm_ref, auth=auth, guestFilePath=script, fileAttributes=attr,
    fileSize=len(data), overwrite=True) 

# data length must equal to the fileSize
# need check response
response = requests.put(file_path, verify=False, data=data)

# ---------------- run execute command ------------------- #
# get process manager
promgr = session._call_method(vim_util,'get_object_property', gopmgr, 'processManager')

# the process to run, return pid
spec = client_factory.create('ns0:GuestProgramSpec')
spec.programPath = '/usr/bin/bash'
spec.arguments = script

result = 'nothing'
result = session._call_method(session.vim, "StartProgramInGuest", promgr, vm=vm_ref, auth=auth, spec=spec)

print result
# print runtime
