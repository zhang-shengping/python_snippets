#!/usr/bin/env python
#!-*- coding:utf-8 -*-

from openstack import connection
import datetime
import re

EVENTS = ['.*\.end$']
URL = 'http://10.0.192.18:35357/v3'
USER = 'shengping'
PROJECT = 'shengping-project'
PASSWORD = 'XXXXXX'
USER_DOMAIN = 'default'
PROJECT_DOMAIN = 'default'

class Event(object):
    def __init__(self, project_id=None, user_id=None,
	         resource_id=None, event_type=None,
                 generated=None, traits=None):
        self.project_id = project_id
        self.user_id = user_id
        self.resource_id = resource_id
        self.event_type = event_type
        self.generated = generated
        self.traits = traits

    # remove the key word if output excel
    def __str__(self):
        desc = 'event_type: {}; project_id: {}; user_id: {}; ' \
               'resource_id: {}; generated: {}; traits {}'.format(
               self.event_type, self.project_id, self.user_id,
               self.resource_id, self.generated, self.traits)
        return desc

def get_conn():
    conn = connection.Connection(auth_url=URL,
                                 project_name=PROJECT,
                                 username=USER,
                                 password=PASSWORD,
                                 user_domain_name=USER_DOMAIN,
                                 project_domain_name=PROJECT_DOMAIN)
    return conn

def get_events():
    conn = get_conn()
    conn.authorize()
    return conn.telemetry.get_events(limit=10000000)

def event_filter(elist):
    def wrapper(func):
        def _inner(es):
            _es = (e for e in es if
                   [p for p in elist if
                    re.search(p, e.event_type)])
            return func(_es)
        return _inner
    return wrapper

def sort_filter(func):
    def _sort_time(es):
        _es = sorted(es, key=lambda e: e.generated)
        return func(_es)
    return _sort_time

#@event_filter(EVENTS)
def state_filter(events):
    for e in events:
        _event = Event()
        for t in e.traits:
            if 'tenant_id' == t.get('name'):
                _event.project_id = t.get('value')
            elif 'user_id' == t.get('name'):
                _event.user_id = t.get('value')
            elif 'instance_id' == t.get('name'):
                _event.resource_id = t.get('value')
            elif 'resource_id' == t.get('name'):
                _event.resource_id = t.get('value')
            elif 'image_id' == t.get('name'):
                _event.resource_id = t.get('value')
            else:
                # other arbitary attributes
                _event.__dict__[t.get('name')] = t.get('value')
            _event.generated = e.generated
            _event.event_type = e.event_type
            _event.traits = e.traits
        yield _event

#@sort_filter
def aggregate(events):
    edict = {}
    #test = []
    for _e in events:
    #    print _e.event_type
    #    if _e.event_type == "compute.instance.create.start":
    #       test.append(_e)
    #       print
    #print len(test)
        eid = _e.resource_id
        if eid:
            if eid in edict:
                edict[eid].append(_e)
            else:
                edict[eid]=[_e]
    return edict

#@event_filter(EVENTS)
#@sort_filter
def to_txt(sth):
    with open('events_log.txt', 'w') as logfile:
        logfile.write('event_type; project_id; user_id; ' \
                      'resource_id; generated \n')
        for _ in sth:
            logfile.write(str(_)+'\n')

if __name__ == '__main__':
    events = get_events()
    _events = list(state_filter(events))
    e = aggregate(_events)
    for k,v in e.items():
        print k
        for x in v:
            print x.event_type
    #to_txt(_events)
