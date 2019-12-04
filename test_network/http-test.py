import eventlet
eventlet.monkey_patch()

import requests
import random
import datetime
import string
from geoip import geolite2


USER_AGENTS = ( 
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_0; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.678.0 Safari/534.21",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:0.9.2) Gecko/20020508 Netscape6/6.1",
    "Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5",
    "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10"
)

NORMAL_URIS = [
    "/",
    "/user",
    "/user/authorize",
    "/user/login",
    "/user/create",
    "/user/delete",
    "/test/delete",
    "/list/prices.php",
    "/list/users.php",
    "/list/photographer.php",
    "/list/paintings.php",
    "/download/products/demo.jpeg",
    "/download/info/demo.ico",
    "/download/ticket/demo.png",
]

NGINX_URIS = [
    "/nginx_plusgins/giom.js",
    "/nginx_plusgins/rsms.js",
    "/nginx_plusgins/kaltura.js",
    "/nginx_plusgins/openresty.js",
    "/nginx_plusgins/atomx.js",
    "/nginx_plusgins/nginx-clojure.js",
    "/nginx_plusgins/openresty.js"
]

VIRUS_NAMES = (
    "macro",
    "script"
)

VIRUS_SUFFIXS = (
    "exe",
    "c",
    "py"
)

USERS = (
    "Bob",
    "Alice",
    "Tom",
    "Jerry",
    "Amber",
    "Will",
)

def random_query_name(num):
  letters = string.ascii_letters
  length = num
  rand_source = ''.join(random.choice(letters) for i in range(length))
  return rand_source

ACTIONS = (
    "/search/thing?id=",
    "/create/thing?id=",
    "/add/thing?id=",
    "/update/thing?id=",
    "/delete/thing?id="
)
ACTIONS_URIS = [random.choice(ACTIONS) + random_query_name(10)   for i in range(50)]

DOMAIN = "http://nginx-website.com"
# DOMAIN = "http://ng1.com"
SOURCE = ['.'.join((str(random.randint(1,254)) for _ in range(4))) for _ in range(100)]
GEO_SOURCE = [ip for ip in SOURCE if geolite2.lookup(ip)]

def fetch(num):
    ALL_URIS = []
    rand_virus = '/' + random.choice(VIRUS_NAMES) + '/' + random_query_name(6) + '.' + random.choice(VIRUS_SUFFIXS)
    user = random.choice(USERS)
    ALL_URIS = NORMAL_URIS + ACTIONS_URIS + NGINX_URIS + [rand_virus]
    domain = DOMAIN + random.choice(ALL_URIS) 
    spoof_src = random.choice(SOURCE)
    user_agent = random.choice(USER_AGENTS)
    cookie = random_query_name(15)
    headers = {
               'X-Forwarded-For':spoof_src, 
               'User-Agent':user_agent,
               'Cookie':cookie,
              }
    
    # (NOTE) pzhang: test for event sleep in coroutines
    # if num == 1:
         # headers = {'X-Forwarded-For':"test", 'User-Agent': "test"}
         # eventlet.sleep(20)
    print "domain is: " + domain
    methods = [requests.get, requests.patch, requests.put, requests.post, requests.delete]  
    request_action = random.choice(methods)
    # r = requests.get(domain, headers=headers, auth=(user,'pass'), timeout=20)
    r = request_action(domain, headers=headers, auth=(user,'pass'), timeout=20)
    print r
    return r

pool = eventlet.GreenPool(1000)
for r in range(600): 
    pool.spawn(fetch, r)
    # (NOTE) pzhang: this will block everything, since it is not in corountine
    # if r == 1:
    #     eventlet.sleep(20)
pool.waitall()
print "finished %s"%datetime.datetime.now()
