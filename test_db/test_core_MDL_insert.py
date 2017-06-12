#!/usr/bin/env python
# encoding: utf-8

from test_core_DDL import *

connection = engine.connect()

# 方法一
ins = cookie.insert().values(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity="12",
    unit_cost="0.50")

# print str(ins)
# print
# print ins.compile().params

# result = connection.execute(ins)
# print result.inserted_primary_key

from sqlalchemy import insert
# 方法二
ins = insert(cookie).values(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity="12",
    unit_cost="0.50"
)

# result = connection.execute(ins)
# print result.inserted_primary_key

# 方法三
ins = cookie.insert()
# result = connection.execute(
    # ins,
    # cookie_name='dark chocolate chip',
    # cookie_recipe_url='http://some.aweso.me/cookie/recipe_dark.html',
    # cookie_sku='CC02',
    # quantity='1',
    # unit_cost='0.75'
# )
# print result.inserted_primary_key

# 使用 Core 插入多行
inventory_list = [
    {'cookie_name': 'peanut butter',
     'cookie_recipe_url': 'http://some.aweso.me/cookie/peanut.html',
     'cookie_sku': 'PB01',
     'quantity': '24',
     'unit_cost': '0.25'},
    # 之后的字典键要和第一个字典键保持一致
    {'cookie_name': 'oatmeal raisin',
     'cookie_recipe_url': 'http://some.okay.me/cookie/raisin.html',
     'cookie_sku': 'EWW01',
     'quantity': '100',
     'unit_cost': '1.00'}
]
result = connection.execute(ins, inventory_list)
# 当插入多个值时，返回值中没有 inserted_primary_key
# print result.inserted_primary_key


