#!/usr/bin/env python
# encoding: utf-8

from ceilometerclient import client as cclient
from keystoneauth1 import loading as ks_loading
from oslo_config import cfg


CEILOMETER_COLLECTOR_OPTS = 'ceilometer_collector'
ks_loading.register_session_conf_options(
    cfg.CONF,
    CEILOMETER_COLLECTOR_OPTS
)

ks_loading.register_auth_conf_options(
    cfg.CONF,
    CEILOMETER_COLLECTOR_OPTS
)

CONF = cfg.CONF

auth = ks_loading.load_auth_from_conf_options(
    CONF,
    CEILOMETER_COLLECTOR_OPTS
)

session = ks_loading.load_session_from_conf_options(
    CONF,
    CEILOMETER_COLLECTOR_OPTS,
    auth=auth
)

_conn = cclient.get_client('2', session=session)
print _conn
