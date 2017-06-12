#!/usr/bin/env python
# encoding: utf-8

from test_core_DDL import *
from sqlalchemy.sql import select
from sqlalchemy import desc

connection = engine.connect()

# 方法一
# select 接受一个 columns list 或者一个table object
s = select([cookie])
# ResultProxy
rp = connection.execute(s)
result = rp.fetchall()

# print result

# 方法二
s = cookie.select()
# ResultProxy
rp = connection.execute(s)
# print type(rp)
# 结果集
# result = rp.fetchall()

# Get the first row of the Result
# print result[0]
# Access column by index.
# print result[0][1]
# Access column by name.
# print result[0].cookie_name
# Access column by Column object.
# print result[0][cookie.c.cookie_name]

# 方法三可以做一个 iterator
# 一个 rp 只能迭代一次
# for row in rp:
    # print row.cookie_name
# print

# 结果集提供的几种方法:

# Returns the first record if there is one and closes the connection.
# 在执行完后连接将断开, 当连接断开时，rp 就不再可用
# 不可以用来判断 table 中是否只有一条记录
# 返回第一条记录，row
# print rp.first()
# print rp.first()

# Returns a single value if a query results in a single record with one column.
# 执行完后连接将会断开。rp 不再可用
# 返回第一条记录的第一列。
# sc = rp.scalar()
# print sc


# Returns one row, and leaves the cursor open for you to make additional fetch calls.
# 可以连续取值迭代
# 如果只是查询第一个值，尽量使用first，first 执行完后会关闭连接，而fetchone不会
# print rp.fetchone()
# print rp.fetchone()
# print rp.fetchone()

# 返回一个 table 有哪些 columns
# print rp.keys()

# 计算多少行记录
# print rp.rowcount

# 控制query

# 选择指定 columns
# s = select([cookie.c.cookie_name, cookie.c.quantity])
# rp = connection.execute(s)
# print rp.keys()
# print rp.first()

# 排序，
s = select([cookie.c.cookie_name, cookie.c.quantity])
# s = s.order_by(cookie.c.quantity)
# 逆序调用 desc
s = s.order_by(desc(cookie.c.quantity))
rp = connection.execute(s)
for row in rp:
    print row
print

# 限制
s = select([cookie.c.cookie_name, cookie.c.quantity])
s = s.limit(2)
rp = connection.execute(s)
print rp.rowcount
for row in rp:
    print row

# 内建函数
from sqlalchemy.sql import func
s = select([func.sum(cookie.c.quantity)])
rp = connection.execute(s)
print rp.scalar()
print rp.keys()

s = select([func.count(cookie.c.cookie_name)])
rp = connection.execute(s)
print rp.keys()
print rp.rowcount
record = rp.first()
print record.keys()
print record.count_1
# print rp.first()
# print rp.first().keys()
# print rp.first().count_1

# 使用label
s = select([func.count(cookie.c.cookie_name).label('inventory_count')])
rp = connection.execute(s)
record = rp.first()
print(record.keys())
print(record.inventory_count)
