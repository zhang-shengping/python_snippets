# -*- coding: utf-8 -*-

import eventlet.patcher
eventlet.patcher.monkey_patch()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy

try:
    import MySQLdb
except ImportError:
    MySQLdb = None


def get_engine(conf):
    connection_dict = sqlalchemy.engine.url.make_url(conf.database.connection)

    engine_args = {
        "pool_recycle": conf.database.sql_idle_timeout,
        "echo": False,
    }

    if "sqlite" in connection_dict.drivername:
        engine_args["poolclass"] = sqlalchemy.pool.NullPool

    elif MySQLdb and "mysql" in connection_dict.drivername:

        pool_args = {
            "db": connection_dict.database,
            "passwd": connection_dict.password,
            "host": connection_dict.host,
            "user": connection_dict.username,
            "min_size": conf.database.sql_min_pool_size,
            "max_size": conf.database.sql_max_pool_size,
            "max_idle": conf.database.sql_idle_timeout,
        }
        creator = eventlet.db_pool.ConnectionPool(MySQLdb, **pool_args)

        engine_args["pool_size"] = conf.database.sql_max_pool_size
        engine_args["pool_timeout"] = conf.database.sql_pool_timeout
        engine_args["creator"] = creator.create

    return sqlalchemy.create_engine(conf.database.sql_connection, **engine_args)

class Connection(object):

    __instance = None

    def __new__(cls, conf):
        if not isinstance(cls.__instance, cls):
            cls.__instance = super(Connection, cls).__new__(cls)
            cls.__instance.engine = get_engine(conf)
            cls.__instance.base = declarative_base(cls.__instance.engine)
            cls.__instance.sessionmaker = sessionmaker(bind=cls.__instance.engine)
        return cls.__instance

    @property
    def session(self):
        # return a new session everytime
        return self.sessionmaker()

if __name__ == "__main__":

    for i in range(10):
        a = Connection('mysql+pymysql://root:stackdb@127.0.0.1/neutron?charset=utf8')
        s = a.session
        print id(a)
        print id(a.engine)
        print id(s)
        print
