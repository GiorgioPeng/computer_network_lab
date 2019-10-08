#!/usr/bin/python
# -*- coding: UTF-8 -*-
from socket import *
import os
import sys
import struct
import time
import select
import binascii


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages

def handle_error(type,code):
	if type == 0 and code == 0:
		return 0
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
		return -1
def checksum(string):
	csum = 0
	countTo = (len(string) // 2) * 2
	count = 0

	while count < countTo:
		thisVal = string[count+1] * 256 + string[count]
		csum = csum + thisVal
		csum = csum & 0xffffffff
		count = count + 2

	if countTo < len(string):
		csum = csum + string[len(string) - 1]
		csum = csum & 0xffffffff

	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum
	answer = answer & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)

	if sys.platform == 'darwin':
		answer = htons(answer) & 0xffff
	else:
		answer = htons(answer)

	return answer

def chesksum(data):
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

def receiveOnePing(icmpSocket, destinationAddress, ID, timeout,send_time):
	# 1. Wait for the socket to receive a reply
	reply = select.select([icmpSocket],[],[],float(timeout))
	if reply[0] == []:
		return 'timeout'
	# 2. Once received, record time of receipt, otherwise, handle a timeout
	receive_time = time.time()
	# 3. Compare the time of receipt to time of sending, producing the total network delay

	# 4. Unpack the packet header for useful information, including the ID
	receive_packet = icmpSocket.recvfrom(1024)
	icmpHeader = receive_packet[0][20:28]
	type, code, cksum, id, seq = struct.unpack(">BBHHH", icmpHeader)
	# 5. Check that the ID matches between the request and reply
	if handle_error(type,code) == 0 and id == ID:
	# 6. Return total network delay
		return receive_time - send_time
	else:
		return handle_error(type,code)

def sendOnePing(icmpSocket, destinationAddress, ID,seq):
	# 1. Build ICMP header
	type = ICMP_ECHO_REQUEST
	code = 0
	cksum = 0
	id = ID
	send_time = time.time()
	body_data = b'testtesttesttesttesttesttesttest'
	# 2. Checksum ICMP packet using given function
	packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)
	cksum = chesksum(packet)
	# 3. Insert checksum into packet
	packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)
	# 4. Send packet using socket
	icmpSocket.sendto(packet,(destinationAddress,80))
	# 5. Record time of sending
	return send_time

def doOnePing(destinationAddress, timeout, seq):
	# 1. Create ICMP socket
	s = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))
	# 2. Call sendOnePing function
	send_time = sendOnePing(s,destinationAddress,os.getpid(),seq)
	# 3. Call receiveOnePing function
	receive_time = receiveOnePing(s,destinationAddress,os.getpid(),timeout,send_time)
	# 4. Close ICMP socket
	s.close()
	if type(receive_time) == type('a'):
		return receive_time
	# 5. Return total network delay
	if receive_time>float(timeout):
		return 'timeout'
	else:
		return receive_time

def ping(*arg):
	# 1. Look up hostname, resolving it to an IP address
	print("now we are pinging [{}], by a 32 bytes data".format(arg[0][0]))
	delay_list = []
	for i in range(int(arg[0][2])):
		# 2. Call doOnePing function, approximately every second
		delay = doOnePing(arg[0][0],arg[0][1],i)
		if type(delay) != type('a'):
			delay_list.append(delay)
		# 3. Print out the returned delay
			print("Responses from {}: bytes=32 delay={}ms".format(arg[0][0],int(delay*1000//1)))
		else:
			print(delay)
		# 4. Continue this process until stopped
	if len(delay_list) !=0:
		print('the maximum delay is {}ms, the minimum delay is {}ms, the average delay is {}ms'.format(int(max(delay_list)*1000//1),int(min(delay_list)*1000//1),int(sum(delay_list)/len(delay_list)*1000//1)))

if __name__ == '__main__':
	try:
		if len(sys.argv) == 2:
			sys.argv.append(1)
		if len(sys.argv) == 3:
			sys.argv.append(4)
		sys.argv[1] = gethostbyname(sys.argv[1])
		ping(sys.argv[1:])
	except:
		print('''an error occur, please make should your input is right!
------------------------------help is showed following
this script can accept three paremeters:
		 		the first one is the destination ip address or domain name,
				the second one which is optional is a suitable timeout,
				the third one which is optional is the times of ping
-------------------------------here is an example:
	python ICMPPing.py lancaster.ac.uk 1 4
-------------------------------
this means you were ping lancaster.ac.uk, and the timeout 1s, the times is 4. And just the first parameter is neccessary.
				''')
