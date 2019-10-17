#!/usr/bin/python
# -*- coding: UTF-8 -*-
from socket import *
import os
import sys
import struct
import time
import select
import binascii
def checksum(data):
	n = len(data)
	m = n % 2
	sum = 0
	for i in range(0, n - m ,2):
		sum += (data[i]) + ((data[i+1]) << 8)
	if m:
		sum += (data[-1])
	sum = (sum >> 16) + (sum & 0xffff)
	sum += (sum >> 16)
	answer = ~sum & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer
def handle_error(type,code):
	if type == 0 and code == 0:
		return ''
	elif type == 3:
		if code == 0:
			return 'network unreachable'
		elif code == 1:
			return 'host unreachable'
		elif code == 2:
			return 'protocol unreachable'
		elif code == 3:
			return 'port unreachable'
		elif code == 4:
			return 'fragmentation needed but no frag. bit set'
		elif code == 5:
			return 'source routing failed'
		elif code == 6:
			return 'destination network unknown'
		elif code == 7:
			return 'destination host unknown'
		elif code == 8:
			return 'source host isolated(obsolete)'
		elif code == 9:
			return 'destination network administratively prohibited'
		elif code == 10:
			return 'destination host administratively prohibited'
		elif code == 11:
			return 'network unreachable for TOS'
		elif code == 12:
			return 'host unreachable for TOS'
		elif code == 13:
			return 'communication administratively prohibited by filtering'
		elif code == 14:
			return 'host procedence violation'
		elif code == 15:
			return 'precedence cutoff in effect'
	elif type == 4 and code == 0:
		return 'source quench'
	elif type == 5:
		if code == 0:
			return 'redirect for network'
		elif code == 1:
			return 'redirect for host'
		elif code == 2:
			return 'redirect for TOS and network'
		elif code == 3:
			return 'redirect for TOS and host'
	elif type == 9 and code ==0:
		return 'router solicitation'
	elif type == 10 and code ==0:
		return 'router solicatation'
	elif type == 11:
		if code == 0:
			return 'TTL equals 0 during transit'
		elif code == 1:
			return 'TTL equals 0 during reassermbly'
	elif type == 12:
		if code == 0:
			return 'IP header bad (catchall error)'
		elif code == 1:
			return 'required potions missing'
	elif type == 13 and code == 0:
		return 'timestamp request(obsolete)'
	elif type == 14:
		return 'timestamp reply(obsolete)'
	elif type == 15 and code == 0:
		return 'information request'
	elif type == 16 and code == 0:
		return 'information reply (obsolete)'
	elif type == 17 and code == 0:
		return 'address mask request'
	elif type == 18 and code == 0:
		return 'address mask reply'
	else:
		return ''

def traceroute(ip_address,timeout=3):
	ttl = 1
	while True:
		send = socket(AF_INET,SOCK_RAW,getprotobyname('icmp'))
		send.setsockopt(IPPROTO_IP,IP_TTL,ttl)
		send.settimeout(timeout)

		type = 8
		code = 0
		cksum = 0
		id = 0
		seq = 0
		body_data = b'testtesttesttesttesttesttesttest'
		packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)
		cksum = checksum(packet)
		packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)

		printResult = ''
		tempIP = '' # the ip between the source IP and the destination IP
		tries = 3
		printTime = 1
		while tries > 0:
			send.sendto(packet,(ip_address,0))
			sendTime = time.time() # the sending time

			try: # try to find some packet whose ttl equals 0
				reply = select.select([send],[],[],timeout)
				receiveTime = time.time()
				if reply[0] == []:
					printResult += '*	'

				receiveData = send.recvfrom(1024)
				type, code, cksum, id, seq = struct.unpack(">BBHHH", receiveData[0][20:28])
				if printTime == 1:
					printResult = handle_error(type,code)+'	'+printResult
					printTime -= 1
				if timeout < receiveTime-sendTime:
					printResult += '*	'
				else:
					temp = int((receiveTime-sendTime)*1000+0.5)
					if temp == 0:
						temp = 1
					printResult += str(temp)+'ms	'
					tempIP = receiveData[1][0]
				tries -= 1
			except error as er:
				# sometimes the packet will lost, and we can catch the exception
				tries -= 1
		if tempIP == '':
			printResult = 'packet lost	'+printResult
		else:
			try:
				domain = gethostbyaddr(tempIP)
				printResult += domain[0]
				printResult += '['+tempIP+']'
			except error as e:
				printResult += tempIP
		printResult = str(ttl)+'	'+printResult
		print(printResult)
		ttl+=1
		send.close()
		if ttl == 256:
			break
		if tempIP == ip_address:
			print("finished")
			break
	return

if __name__ == '__main__':
	dest = input('please input the destination:\n')
	timeout = input("please input the timeout:\n")
	try:
		ip_address = gethostbyname(dest)
		print('tracing: '+dest+' ['+ip_address+']')
		traceroute(ip_address,int(timeout))
	except ValueError as v:
		print("Please input a integer timeout")
	except gaierror as g:
		print('wrong destination')
