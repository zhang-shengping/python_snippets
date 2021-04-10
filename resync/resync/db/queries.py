# -*- coding: utf-8 -*-

from f5_openstack_agent.lbaasv2.drivers.bigip.resync.db import models

class Queries(object):

    def __init__(self):
        self.session = models.con.session

        self.lb = models.Loadbalancer
        self.ls = models.Listener
        self.pl = models.Pool
        self.mn = models.Monitor
        self.mb = models.Member

    def get_loadbalancer(self, lb_id):
        return self.session.query(self.lb).get(lb_id)

    def get_listener(self, ls_id):
        return self.session.query(self.ls).get(ls_id)

    def get_pool(self, pl_id):
        return self.session.query(self.pl).get(pl_id)

    def get_mn(self, mn_id):
        return self.session.query(self.mn).get(mn_id)

    def get_member(self, mb_id):
        return self.session.query(self.mb).get(mb_id)
