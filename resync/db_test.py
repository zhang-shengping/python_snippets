# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import  backref
import sqlalchemy as sa

# engine = create_engine('mysql+pymysql://neutron:Duw2FhafDsggQQHdWbehecD2v@10.250.22.53/ovs_neutron?read_default_group=tripleo&read_default_file=/etc/my.cnf.d/tripleo.cnf', echo=True)
# engine = create_engine('mysql+pymysql://root:stackdb@127.0.0.1/neutron?charset=utf8', echo=True)
engine = create_engine('mysql+pymysql://root:stackdb@127.0.0.1/neutron?charset=utf8')
Base = declarative_base(engine)
########################################################################


class Loadbalancers(Base):
    __tablename__ = 'lbaas_loadbalancers'
    __table_args__ = {'autoload':True}

class Listeners(Base):
    __tablename__ = 'lbaas_listeners'
    __table_args__ = {'autoload':True}

    # loadbalancer_id = Column("loadbalancer_id", String(255))

class Pools(Base):
    __tablename__ = 'lbaas_pools'
    __table_args__ = {'autoload':True}
    # members = relationship("Members",
                           # backref=backref("pools", uselist=False))
    healthmonitor_id = Column(String, ForeignKey('lbaas_healthmonitors.id'))
    # loadbalancer_id = Column("loadbalancer_id", String(255))

    members = relationship("Members")
    healthmonitor = relationship("Monitors", uselist=False)

class Members(Base):
    __tablename__ = 'lbaas_members'
    __table_args__ = {'autoload':True}
    pool_id = Column(String, ForeignKey('lbaas_pools.id'))
    # pool = relationship("Pools")

class Monitors(Base):
    __tablename__ = 'lbaas_healthmonitors'
    __table_args__ = {'autoload':True}

def loadSession():
    """"""
    # metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == "__main__":
    pool_id = "ffaebc6e-c428-4f39-8fd8-29d5f809f699"
    session = loadSession()
    # res = session.query(Members).filter(Members.id == "000cbd56-b9b6-40bf-9429-1847ef606c0c")
    # res = session.query(Members).get("000cbd56-b9b6-40bf-9429-1847ef606c0c")
    import pdb; pdb.set_trace()
    res = session.query(Pools).get(pool_id)
    # res = session.query(Members).get("027d4f24-007c-414f-8188-de7944eaf794")
    print "---------"
    print res.members
    print "---------"
    print res.members[0].address
    print res.members[0].protocol_port
    print "---------"
    print res.healthmonitor.type
    print "---------"
    print "*********"
    lb_id = "b2d6bdc3-d08c-48d9-8676-a39229e7148d"
    # res = session.query(Pools).filter_by(loadbalancer_id == lb_id).all()
    res = session.query(Pools).filter(Pools.loadbalancer_id == lb_id)
    res = res.all()
    print res

    # res = session.query(Members).get("027d4f24-007c-414f-8188-de7944eaf794")
    # print "---------"
    # print res.pool
    # print "---------"
    # print res[1].id
