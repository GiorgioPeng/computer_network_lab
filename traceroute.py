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

def traceroute(ip_address):
	print('tracing: '+ip_address)
	ttl = 1
	while True:
		send = socket(AF_INET,SOCK_RAW,getprotobyname('icmp'))
		send.setsockopt(IPPROTO_IP,IP_TTL,ttl)
		send.settimeout(3)

		type = 8
		code = 0
		cksum = 0
		id = 0
		seq = 0
		body_data = b'testtesttesttesttesttesttesttest'
		packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)
		cksum = checksum(packet)
		packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)


		printResult = str(ttl)+'	'
		tempIP = '' # the ip between the source IP and the destination IP
		tries = 3
		while tries > 0:
			send.sendto(packet,(ip_address,0))
			sendTime = time.time() # the sending time

			try: # try to find some packet whose ttl equals 0
				reply = select.select([send],[],[],3)
				receiveTime = time.time()
				if reply[0] == []:
					printResult += '*	'

				receiveData = send.recvfrom(1024)
				if 3 < receiveTime-sendTime:
					printResult += '*	'
				else:
					printResult += str(int((receiveTime-sendTime)*1000))+'ms	'
					tempIP = receiveData[1][0]
				tries -= 1
			except error as er:
				# sometimes the packet will lost, and we can catch the exception
				tries -= 1
		if tempIP == '':
			printResult += 'timeout'
		else:
			printResult += tempIP
		print(printResult)
		ttl+=1
		send.close()
		if tempIP == ip_address:
			break
	return
if __name__ == '__main__':
	dest = input('please input the destination:\n')
	try:
		ip_address = gethostbyname(dest)
		traceroute(ip_address)
	except:
		print('wrong destination')
