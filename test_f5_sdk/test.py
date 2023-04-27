# -*- coding: utf-8 -*-

from f5.bigip import ManagementRoot
from f5.bigip.contexts import TransactionContextManager

b = ManagementRoot('10.145.75.236', 'admin', 'admin@f5.com')
tx = b.tm.transactions.transaction
with TransactionContextManager(tx) as api:
    api.tm.ltm.pools.pool.create(name='testpool1')
    api.tm.ltm.virtuals.virtual.create(name='testvip', pool='testpool1', destination='192.168.102.99:80')
