#!/usr/bin/env python
# encoding: utf-8

# import futurist
from futurist import periodics
import time

started_at = time.time()

# add cache time to change started_at
@periodics.periodic(2592000)
def every_one(started_at):
    print("1: %s" % (time.time() - started_at))

callables = [(every_one, (started_at,), {}),]
w = periodics.PeriodicWorker(callables)

if __name__ == "__main__":
    w.start()


