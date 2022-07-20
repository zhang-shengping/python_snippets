# -*- coding: utf-8 -*-
import eventlet
eventlet.monkey_patch()

import urllib3
import json

urls = ["https://google.com/"] * 20

if __name__ == "__main__":
    http = urllib3.PoolManager(num_pools=2, maxsize=1000)
    pool = eventlet.greenpool.GreenPool()

    for url in urls:
        pool.spawn(http.request, 'GET', url)

    pool.waitall()
