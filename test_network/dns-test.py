# import eventlet
# eventlet.monkey_patch()

from geoip import geolite2
from scapy.all import *
import string
import random


QUERY_NAMES = [
  "google.com",
  "www.website.com",
  "baidu.com",
  "onion.com",
  "website.com",
]

def random_query_name():
  letters = string.ascii_letters
  length = random.randint(1,254)
  rand_source = ''.join(random.choice(letters) for i in range(length))
  QUERY_NAMES.append(rand_source)
  return random.choice(QUERY_NAMES)


def random_sources():
  SOURCE = ['.'.join((str(random.randint(1,254)) for _ in range(4))) for _ in range(100)]
  return [ip for ip in SOURCE if geolite2.lookup(ip)]
  

for source_ip in random_sources():
  query_name = random_query_name()
  packet = IP(src=source_ip, dst="10.10.1.37")/UDP(sport=RandShort(),dport=53)/DNS(rd=1,qd=DNSQR(qname=query_name))
  answer = sr1(packet)
  print answer[DNS].summary()
