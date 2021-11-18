# -*- coding: utf-8 -*-

from tooz import coordination

coordinator = coordination.get_coordinator('memcached://127.0.0.1:11211', b'host-1')
coordinator.start()

# Create a lock
lock = coordinator.get_lock("foobar")
with lock:
    print("Do something that is distributed")

coordinator.stop()
