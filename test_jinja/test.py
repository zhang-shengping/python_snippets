# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader

import os


work_dir = os.getcwd()
templates_dir = work_dir + '/templates'

env = Environment(
    loader=FileSystemLoader(templates_dir)
)

template = env.get_template('child-template.txt')
output = template.render({"name":"Peter Zhang", "jinja_name":"JINJA 2"})
print output

