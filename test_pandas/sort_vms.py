#!/usr/bin/env python
# encoding: utf-8

import pandas as pd

df = pd.read_csv('zabbix_data_convert.csv', header=0, index_col='host_name')

# print df.describe()
# print df.head()
# print df.columns
# print df.dtypes
# print df.index
# print df['top1']
# print df[0:10]

def host_value(df):
    # 对行处理
    df = df.dropna(axis=0, how='any')
    df = df[df.index.duplicated(keep='last')]

    # 对列处理
    columns = df.columns.tolist()
    columns.pop(0)

    for i, r in df.iterrows():
        for t in columns:
            value = r[t]
            # if type(value) == str:
                # yield i, value
            #yield type(value)
            yield i,float(value.split('(')[0])

host_list = host_value(df)
# sorted with key
result = sorted(host_list, key=lambda x:x[1])
# list slice
print result[-1:-11:-1]

