# -*- coding: utf-8 -*-

# from keystoneauth1.identity import v3
from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client

username = 'admin'
password = 'nomoresecret'
project_name = 'admin'
project_domain_id = 'default'
user_domain_id = 'default'
# auth_url = 'http://auth.example.com:5000/v3'
# auth_url = 'http://10.145.73.17:5000/v3'
auth_url = 'http://10.145.73.17/identity'
# auth = v3.Password(auth_url=auth_url,
auth = identity.Password(auth_url=auth_url,
                         username=username,
                         password=password,
                         project_name=project_name,
                         project_domain_id=project_domain_id,
                         user_domain_id=user_domain_id,
                         )

sess = session.Session(auth=auth)
neutron = client.Client(session=sess)

re = neutron.list_loadbalancers( id='0044f8f2-e547-4415-bee9-feecd17628b1')

print("---- loadbalancers ----")
for _ in re['loadbalancers']:
    print _

re = neutron.list_listeners( id='b015d913-c996-443f-b332-33146514341e')

print("---- listeners ----")
for _ in re['listeners']:
    print _

import pdb; pdb.set_trace()
re = neutron.list_lbaas_pools()

print("---- pools ----")
for _ in re['pools']:
    print _

re = neutron.show_lbaas_pool('8755a316-b066-4194-b31c-91fec94c7d47')
print(re)

# re = neutron.list_members( id='8755a316-b066-4194-b31c-91fec94c7d47')

# print("---- pools ----")
# for _ in re['pools']:
    # print _
