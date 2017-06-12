#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, Numeric, String, ForeignKey
from sqlalchemy import DateTime


engine = create_engine('mysql+pymysql://ecollector:password'
                       '@localhost/ecollector', pool_recycle=3600)
#connection = engine.connect()

metadata = MetaData()

cookie = Table('cookies', metadata,
               Column('cookie_id', Integer(), primary_key=True),
               Column('cookie_name', String(50), index=True),
               Column('cookie_recipe_url', String(255)),
               Column('cookie_sku', String(55)),
               Column('quantity', Integer()),
               Column('unit_cost', Numeric(12, 2)))

users = Table('users', metadata,
              Column('user_id', Integer(), primary_key=True),
              Column('username', String(15), nullable=False, unique=True),
              Column('email_address', String(255), nullable=False),
              Column('phone', String(20), nullable=False),
              Column('password', String(25), nullable=False),
              Column('created_on', DateTime(), default=datetime.now),
              Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now))

orders = Table('orders', metadata,
               Column('order_id', Integer(), primary_key=True),
               Column('user_id', ForeignKey('users.user_id')))

line_items = Table('line_items', metadata,
                   Column('line_items_id', Integer(), primary_key=True),
                   Column('order_id', ForeignKey('orders.order_id')),
                   Column('cookie_id', ForeignKey('cookies.cookie_id')),
                   Column('quantity', Integer()),
                   Column('extended_cost', Numeric(12, 2)))

metadata.create_all(engine)





