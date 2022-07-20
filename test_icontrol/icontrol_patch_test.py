# -*- coding: utf-8 -*-
import eventlet
eventlet.monkey_patch()

import urllib3
import json

# url = "https://10.144.73.244/restui/default/default.html?$display=/mgmt/tm/ltm/virtual-address/~Project_8a2d7296ae9b4bd4a412eb3cb9aa680e~Project_b7937afc-700e-45e6-957f-551509de5e39#/"
# url = "https://10.144.73.244:443/mgmt/tm/ltm/virtual/"
vss=[
    "Project_0ef86f5b-59ab-4036-b460-035fba7cbae2",
    "Project_3f195cbd-142e-435d-9a17-90e57706c892",
    "Project_6ab06598-7088-4ce6-96f4-6ff7569cd9a0",
    "Project_6b549174-76a2-46be-a262-361efd92bdce",
    "Project_6e371111-0f27-4ea1-a499-105a417f6be9",
    "Project_7a86e7cd-71d8-4125-9d58-c9c5f12f8465",
    "Project_8a4f72a8-96c7-4b96-9778-1f681a5ba94b",
    "Project_9c8ca9f1-6096-4144-8793-be62af72ea9e",
    "Project_9e9a8c18-26d7-498e-8505-3a4c3ffe0a4d",
    "Project_60cdf34f-c98a-4244-9461-28df608cc317",
    "Project_61df2fa8-2dea-4f71-8ef5-52f202e1ba6a",
    "Project_68bbb93f-a7e1-4418-b57b-b20aa4a1e5d9",
    "Project_70c226e1-8c76-46cf-b5a4-1f47ddadde28",
    "Project_92efa484-dcdf-449c-a073-0effcc558ff0",
    "Project_101f6e2d-1b46-4aeb-9f94-14a48316166f",
    "Project_310c1187-f097-4151-9d71-4b8c6199ba33",
    "Project_461ac5e9-1702-4713-b537-ba1255fdffec",
    "Project_559c0d89-49b0-4605-a580-c80c6a912b48",
    "Project_585cece0-dac0-4aec-a1b2-7f20a41b978c",
    "Project_3188bd4e-fa4f-4c92-8a4a-f3449a0fc500",
    "Project_5011addc-cdbc-4bac-8203-04d7d5129a5f",
    "Project_76251c46-c956-40b6-ad83-05eb9cfd4a7d",
    "Project_257585e8-3c55-420c-9776-35899fe1522c",
    "Project_06241232-bc60-4c42-a3e2-df5083ec7b4c",
    "Project_9436767a-78f2-4b60-8b3b-1f3961b9c618",
    "Project_12654110-2cda-4f20-9475-d3d81bcfa7a5",
    "Project_47875420-56ac-4fdc-9d99-38eda2168a14",
    "Project_92856362-1f99-4813-8adb-c440aa909bde",
    "Project_a31d1a4e-fc24-42e4-9a09-826a7e2f5577",
    "Project_b2d801de-ab02-4463-92da-f6ade458eebe",
    "Project_b4fb8a5d-87fb-4714-b287-7393118f2d42",
    "Project_b6f7799f-f0cc-42a0-92e4-bbe48415a26f",
    "Project_b7dcf476-2485-4b8d-94f7-1f52e6dd0030",
    "Project_b58daf0d-21b2-4cba-9663-228433eb16fd",
    "Project_b60a949f-eaf9-4c19-9b68-1771edbffa5d",
    "Project_b90ab0bf-ac2b-4a4c-8bb9-f5da4c58f506",
    "Project_bc26abea-164a-4662-8a88-650d6d3332b5",
    "Project_bca940af-b41b-4c70-b64b-8f1b37f5a0fb",
    "Project_c2d89446-4dfd-4075-a00f-7a23a97c7948",
    "Project_c45f92e1-009a-42b6-8609-5e5af13d2594",
    "Project_c7351b2d-7b28-4344-99df-b4f649e8eeb8",
    "Project_cfd09d14-b620-4692-99fb-7c26303ee9e0",
    "Project_d4c4dc32-567d-40e4-a4a4-5cc4b41c7871",
    "Project_d6d0253f-27e4-4aa3-a170-61a242cdb01e",
    "Project_d16ebb26-5589-4a67-b05c-4930e6d7412a",
    "Project_d635fee1-1187-4612-ba31-71044b4ddb28",
    "Project_e3a3d535-8b2b-4cdc-b209-d82132e44cc8",
    "Project_e8e377b8-84be-4a8e-9918-8c14355e9ca1",
    "Project_e14ca822-c434-4af2-b8ee-42ffaac423eb",
    "Project_f837fc67-8804-4197-af0a-5c825383a2ac"
]

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
    import pdb; pdb.set_trace()
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
        pool.spawn(http.request, 'PATCH', url, headers=headers, body=encoded_data)
        # resp = http.request('PATCH', url, headers=headers, body=encoded_data)
        # print(resp.status)
        # print(resp.data)
    pool.waitall()
