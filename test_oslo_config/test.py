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
    # 不同模块register 对应需要的配置
    cfg.BoolOpt('test', default=False),
]

CONF.register_opts(opts)


if __name__ == "__main__":
    # 如果没有定义默认路径，
    # oslo config 会去搜索/etc目录下同名的test.conf
    # 如果配置了 CONF 的 project参数，则会寻找在 /etc 下
    # 与project 同名的配置文件
    # CONF(default_config_files=['test.conf'])
    CONF(default_config_files=None)
    print(CONF.simple.enable)
    # print(CONF.simple.disable)
    print(CONF.test)
