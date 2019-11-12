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
	for i in range(0, n - m, 2):
		sum += (data[i]) + ((data[i+1]) << 8)
	if m:
		sum += (data[-1])
	sum = (sum >> 16) + (sum & 0xffff)
	sum += (sum >> 16)
	answer = ~sum & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer


def handle_error(type, code):
	'''
	This method is used to distinguish which kind of error occurs or no error occurs

	Parameter:
		type <class 'int'>: the type of ICMP
		code <class 'int'>: the code of ICMP

	Return:
		Normal string: the name of the error
		Null string: there is no error
	'''
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

def traceroute(ip_address, timeout=3):
	'''
	This method is used to trace router

	Parameter:
		ip_address <class 'str'>: the destination of the traceroute
		timeout <class 'int'> [default = 3]: the timeout of each ICMP requst of the traceroute

	Return:
		None
	'''
	# at the begin, set the ttl equal to 1
	ttl = 1
	while True:
		# create the ICMP socket
		send = socket(AF_INET,SOCK_RAW,getprotobyname('icmp'))
		send.setsockopt(IPPROTO_IP,IP_TTL,ttl)
		send.settimeout(timeout)

		# construct the header of the ICMP packet
		type = 8
		code = 0
		cksum = 0
		id = 0
		seq = 0
		body_data = b'testtesttesttesttesttesttesttest'
		packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)
		cksum = checksum(packet)
		packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)

		# the print string
		printResult = ''
		# the ip between the source IP and the destination IP
		tempIP = '' 
		# the try time is 3, which is as same as the tracert at cmd in windows system
		tries = 3
		# printTime is a counter, because the error must be same if we send ICMP packet to one destination, we just need to add the error message once,
		printTime = 1
		while tries > 0:
			# send the packet to the destination
			send.sendto(packet, (ip_address, 0))
			# record the send time
			sendTime = time.time() 

			# try to find some packet whose ttl equals 0
			try: 
				reply = select.select([send], [], [], timeout)
				# record the receive time
				receiveTime = time.time()
				# if the packet is empty, we will print a '*'
				if reply[0] == []:
					printResult += '*	'
					tempTimeout = 9999
				else:
					tempTimeout = timeout

				# receive the data 
				receiveData = send.recvfrom(1024)
				
				# destuct the packet
				type, code, cksum, id, seq = struct.unpack(">BBHHH", receiveData[0][20:28])
				if printTime == 1:
					# add the error message into the print result
					printResult = handle_error(type, code) + '	' + printResult
					printTime -= 1
				# if the delay is greater than the timeout, we will print a '*'
				if tempTimeout < receiveTime-sendTime:
					printResult += '*	'
				# in other situation, we will print the normal delay
				else:
					temp = int((receiveTime-sendTime)*1000+0.5)
					if temp == 0:
						temp = 1
					printResult += str(temp)+'ms	'
					tempIP = receiveData[1][0]
				tries -= 1
			# sometimes the packet will lost, and we can catch the exception
			except error as er:
				tries -= 1
		# if there is no packet which we received, we should think the packets are lost
		if tempIP == '':
			printResult = 'packet lost	'+printResult
		# in other situation, we should try to get its domain
		else:
			try:
				# try to get the domain of the ip
				domain = gethostbyaddr(tempIP)
				printResult += domain[0]
				printResult += '[' + tempIP + ']'
			# if we donot get the domian
			except error as e:
				printResult += tempIP
		# print the result
		printResult = str(ttl)+'	'+printResult
		print(printResult)
		ttl+=1
		send.close()
		# if the ttl equal 256, we should exit, because the greatest ttl is equal to 255
		if ttl == 256:
			break
		# if the packet arrive the destination, we also should exit
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
