# -*- coding: utf-8 -*-

from routes.mapper import Mapper

mapper = Mapper()

mapper.resource(
    "loadbalancers", "loadbalancers", path_prefix = "/lbaas/",
    member={'stats': 'GET', 'statuses': 'GET', "rebuild": "POST"}
)
# import pdb; pdb.set_trace()
ret = mapper.routematch(environ={"REQUEST_METHOD": "POST", "PATH_INFO": "/lbaas/loadbalancers/test/rebuild"})
print(ret)

