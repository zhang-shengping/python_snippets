# -*- coding: utf-8 -*-

from routes.mapper import Mapper

mapper = Mapper()

sub_mapper = mapper.submapper(controller="handle_hobby")
sub_mapper.connect(None, "/hi/test/{name}", action="game")

m_result = mapper.routematch("/hi/test/jack")
print(m_result)


# use prefix

mapper = Mapper()

sub_mapper = mapper.submapper(path_prefix="/use_prefix", controller="handle_fix")

# use path_prefix, first variable is defined as path
# '/' must add before test, or the path will be /use_prefixtest/...
# not default to "GET" method, default to all HTTP METHODS 'GET' 'POST'
sub_mapper.connect("/test/{variable}", action="unit_test")
sub_mapper.connect("/test/{variable}", action="unit_test1")
sub_mapper.connect("/test/{variable}", action="unit_test2")

# this (action after connect) does not work, we must define conditions param in sub_mapper.connect
# sub_mapper.action(action="create", method="POST")

ret1 = mapper.routematch("/use_prefix/test/xyz")
print(ret1)

mapper = Mapper()

sub_mapper = mapper.submapper(path_prefix="/use_prefix", controller="handle_fix")
sub_mapper.action(action='show', method='GET')
sub_mapper.action(action='create', method='POST')

ret2 = mapper.routematch(environ={"REQUEST_METHOD": "POST", "PATH_INFO": "/use_prefix"})
print(ret2)

