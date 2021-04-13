# -*- coding: utf-8 -*-

from f5_openstack_agent.lbaasv2.drivers.bigip.resync import options
from f5_openstack_agent.lbaasv2.drivers.bigip.resync.db import connection
from oslo_config import cfg

from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import relationship

options.load_db_options()
options.parse_options()
conf = cfg.CONF
import pdb; pdb.set_trace()

con = connection.Connection(conf)
Base = con.base
metadata = Base.metadata


class Loadbalancer(Base):
    __tablename__ = 'lbaas_loadbalancers'
    __table_args__ = {'autoload':True}
    
    project_id = Column("project_id")


class Listener(Base):
    __tablename__ = 'lbaas_listeners'
    __table_args__ = {'autoload':True}

    loadbalancer_id = Column("loadbalancer_id")


class Pool(Base):
    __tablename__ = 'lbaas_pools'
    __table_args__ = {'autoload':True, 'extend_existing': True}

    loadbalancer_id = Column("loadbalancer_id")
    healthmonitor_id = Column(String, ForeignKey('lbaas_healthmonitors.id'))

    members = relationship("Member", lazy='subquery')
    healthmonitor = relationship("Monitor", uselist=False, lazy='subquery')


class Monitor(Base):
    __tablename__ = 'lbaas_healthmonitors'
    __table_args__ = {'autoload':True}


class Member(Base):
    __tablename__ = 'lbaas_members'
    __table_args__ = {'autoload':True}

    pool_id = Column(String, ForeignKey('lbaas_pools.id'))
