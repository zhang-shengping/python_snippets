# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re

BaseFile = 'f5.xlsx'
CompFile = 'export_hans.xlsx'


base_df = pd.read_excel(BaseFile, header=None)
comp_df = pd.read_table('f5-hans.csv', encoding='utf-8', sep=',')

base = [(index, v) for index, row in base_df.iterrows() for v in row if v is not np.nan]
comp = [{index: [row[1], row[2], 0]} for index, row in comp_df.iterrows()]

out = []
miss = []
test = []

for b in base:
    # print b[1]
    # import pdb; pdb.set_trace()
    p1 = re.sub(ur'[\uff08|\uff09]', '|', b[1])
    # print p1
    comp_list = p1.split('|')
    # print comp_list
    if len(comp_list) == 1:
        bv = comp_list[0]
    else:
        bv = comp_list[-2]
    # print bv
    # print "--------------"
    # import pdb; pdb.set_trace()
    for c in comp:
        index = c.keys()[0]
        value = c.values()[0]
        comp_value = value[0]
        origin_value = b[1]
        base_value = bv
        if type(comp_value) is unicode and type(base_value) is unicode:
            # t = base_value + ": " + comp_value
            # test.append(t)

            if base_value.lower().strip() in comp_value.lower():
                output = origin_value + ':  ' + value[0] + ' --- ' + value[1]
                value[2] += 1
                out.append(output)
        # else:
        #    import pdb;pdb.set_trace()
        #    if b[1] == value[1]:
        #        output = origin_value + ':' + value[0] + '|' + value[1]
        #        value[2] += 1
        #        out.append(output)

with open('test.txt', 'w') as f:
    for o in test:
        c = o.encode('utf-8')
        f.write(c)
        f.write('\n')

with open('compare.txt', 'w') as f:
    for o in out:
        c = o.encode('utf-8')
        f.write(c)
        f.write('\n')

for c in comp:
    value = c.values()[0]
    if value[2] == 0:
        if type(value[0]) is unicode and type(value[1]) is unicode:
            output = value[0] + " --- " + value[1]
            miss.append(output)

with open('miss.txt', 'w') as f:
    for m in miss:
        c = m.encode('utf-8')
        f.write(c)
        f.write('\n')
