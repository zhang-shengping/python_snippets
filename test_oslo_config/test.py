#!/usr/bin/env python
# encoding: utf-8

from oslo_config import cfg

opt_group = cfg.OptGroup(name='simple')
simple_opts = [
    cfg.BoolOpt('enable', default=False)
]

CONF = cfg.CONF
CONF.register_group(opt_group)
CONF.register_opts(simple_opts, opt_group)

opts = [
    cfg.StrOpt('bind_host', default='0.0.0.0'),
    cfg.PortOpt('bind_port', default=9292),
    # 定义的configure变量都必须register
    cfg.BoolOpt('test', default=False),
]

CONF.register_opts(opts)


if __name__ == "__main__":
    # 如果没有定义默认路径，可以oslo config 会去搜索/etc目录
    # CONF(default_config_files=['test.conf'])
    CONF(default_config_files=None)
    print(CONF.simple.enable)
    # print(CONF.simple.disable)
    print(CONF.test)
