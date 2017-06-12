#!/usr/bin/env python
# encoding: utf-8

from cotyledon import Service
from cotyledon import ServiceManager
from time import sleep

class MyService(Service):
    def __init__(self, worker_id):
        super(MyService, self).__init__(worker_id)
        self.running = True
        self.id = worker_id

    def run(self):
        while self.running:
            print "in {} process".format(self.id)
            sleep(5)

    def terminate(self):
        self.running = False
        print "end {} process".format(self.id)

    def reload(self):
        print "reload {} process".format(self.id)

class MyManager(ServiceManager):
    def __init__(self):
        super(MyManager, self).__init__()
        self.register_hooks(on_reload=self.reload)

        # 5 workers to run MyService
        # self.service_id = self.add(MyService, 5)
        self.service_id = self.add(MyService, 1)

    def reload(self):
        self.reconfigure(self.service_id, 10)

if __name__ == "__main__":
    m = MyManager()
    m.run()



