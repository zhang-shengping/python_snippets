
#!/usr/bin/env python
#-*-encoding:UTF-8-*-
 
from scapy.all import *
from threading import Thread
from Queue import Queue
import random
import string
 
 
USER_AGENTS = (                                               # items used for picking random HTTP User-Agent header value
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_0; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.678.0 Safari/534.21",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:0.9.2) Gecko/20020508 Netscape6/6.1",
    "Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5",
    "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10"
)
 
TOP_DOMAIN = ('com','org','net','gov','edu','mil','info','name','biz')
 
#DOMAIN = ["www.%s.%s" %( 
#        '.'.join(''.join(random.sample(string.ascii_lowercase, random.randint(2,6))) for x in range(random.randint(1,2))),
#         random.choice(TOP_DOMAIN))
#        for _ in range(100)
#]

DOMAIN = "nginx-website.com"
src = "10.10.1.54"
 
 
SOURCE = ['.'.join((str(random.randint(1,254)) for _ in range(4))) for _ in range(100)]
 
class Scan(Thread):
    HTTPSTR = 'GET / HTTP/1.1\r\nUser-Agent: %s\r\nHost: %s\r\nX-Forwarded-For: %s\r\nAccept: */*\r\n'
    def run(self):
        for _ in xrange(1):
            domain = DOMAIN
            spoof_src = random.choice(SOURCE)
            http = self.HTTPSTR % (random.choice(USER_AGENTS), domain, spoof_src)
            print http
            try:
                request = IP(dst=domain)/TCP(sport=50842, dport=80)/http
                # print request
                #request = IP(dst=domain) / TCP(dport=80) / http
                reponse = send(request)
                print response
            except:
                pass
          
task = []
for x in range(1):
    t = Scan()
    task.append(t)
 
for t in task:
    t.start()
 
for t in task:
    t.join()
 
print 'all task done!'
