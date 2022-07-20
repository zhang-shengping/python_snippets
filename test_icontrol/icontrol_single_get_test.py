# -*- coding: utf-8 -*-
import eventlet
eventlet.monkey_patch()

import urllib3
import json

# url = "https://10.144.73.244/restui/default/default.html?$display=/mgmt/tm/ltm/virtual-address/~Project_8a2d7296ae9b4bd4a412eb3cb9aa680e~Project_b7937afc-700e-45e6-957f-551509de5e39#/"
# url = "https://10.144.73.244:443/mgmt/tm/ltm/virtual/"
vss=[
    "Project_0ef86f5b-59ab-4036-b460-035fba7cbae2",
] * 40

urls = [
    "https://10.144.73.244:443/mgmt/tm/ltm/virtual/" + \
    "~" + "Project_8a2d7296ae9b4bd4a412eb3cb9aa680e" + "~" + vs
    for vs in vss
]
# def get_urls(partition, vss):

    # result = []

    # for vs in vss:
        # url = ""
        # url = "https://10.144.73.244:443/mgmt/tm/ltm/virtual-address/" + \
            # "~" + partition + "~" + vs
        # result.append(url)
    # return result

# urls = get_urls("Project_8a2d7296ae9b4bd4a412eb3cb9aa680e", vss)

if __name__ == "__main__":
    # http = urllib3.PoolManager(cert_reqs = "CERT_NONE", num_pools=2, maxsize=1000)
    http = urllib3.PoolManager(num_pools=2, maxsize=1000)

    headers = urllib3.make_headers(basic_auth='admin:Passw0rd@F5')
    headers['Content-Type'] = "application/json"

    body = {"connectionLimit": 123}
    encoded_data = json.dumps(body)

    # resp = http.request('GET', url, headers=headers)
    # for url in urls:
        # resp = http.request('PATCH', url, headers=headers, body=encoded_data)
        # print(resp.status)
        # print(resp.data)

    pool = eventlet.greenpool.GreenPool()

    for url in urls:
        # pool.spawn(http.request, 'PATCH', url, headers=headers, body=encoded_data)
        pool.spawn(http.request, 'GET', url, headers=headers)
        # resp = http.request('GET', url, headers=headers)
        # print(resp.status)
        # print(resp.data)
    pool.waitall()
