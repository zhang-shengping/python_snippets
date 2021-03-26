# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://neutron:Duw2FhafDsggQQHdWbehecD2v@10.250.22.53/ovs_neutron?read_default_group=tripleo&read_default_file=/etc/my.cnf.d/tripleo.cnf', echo=True)
Base = declarative_base(engine)
########################################################################
class Members(Base):
    __tablename__ = 'lbaas_members'
    __table_args__ = {'autoload':True}

def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == "__main__":
    session = loadSession()
    # res = session.query(Members).filter(Members.id == "000cbd56-b9b6-40bf-9429-1847ef606c0c")
    res = session.query(Members).get("000cbd56-b9b6-40bf-9429-1847ef606c0c")
    print "---------"
    print res.id
    print "---------"
    # print res[1].id
