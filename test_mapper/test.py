# -*- coding: utf-8 -*-

from routes.mapper import Mapper

mapper = Mapper()

# default to use "GET"
mapper.connect("/hi", controller="say_hi")
mapper.connect("/hi", controller="say_hi_again")
mapper.connect("/hi/{project_id}", controller="say_bye")
mapper.connect("/bye/:project_id", controller="say_bye_id")
mapper.connect("/bye/:project_id/{name}", controller="say_bye_name")
mapper.connect("/bye/:project_id/test/{alphets:[a-z]+}", controller="say_bye_name")

# use action to tell "POST" or "GET"
mapper.connect("/action", controller="action_test", conditions=dict(method=["GET"]), action="list")
mapper.connect("/action", controller="action_test", conditions=dict(method=["POST"]), action="new")

ret1 = mapper.routematch("/hi")
ret2 = mapper.routematch("/hi/abc")
ret3 = mapper.routematch("/bye/project_bye")
ret4 = mapper.routematch("/bye/project_bye/test")
ret5 = mapper.routematch("/bye/project_bye/test/xyz")
ret6 = mapper.routematch("/bye/project_bye/test/xyz123")

ret7 = mapper.routematch(environ={"REQUEST_METHOD": "POST", "PATH_INFO": "/action"})
ret8 = mapper.routematch(environ={"REQUEST_METHOD": "GET", "PATH_INFO": "/action"})

print(ret1)
print(ret2)
print(ret3)
print(ret4)
print(ret5)
print(ret6)

print(ret7)
print(ret8)
