from scapy.all import *

# answer = sr1(IP(src="30.50.215.62",dst="10.10.1.37")/UDP(sport=RandShort(),dport=53)/DNS(rd=1,qd=DNSQR(qname="nginx-website.com")),verbose=0)
answer = sr1(IP(src="30.50.215.62",dst="10.10.1.37")/UDP(sport=RandShort(),dport=53)/DNS(rd=1,qd=DNSQR(qname="website.com")),verbose=0)
print answer[DNS].summary()
