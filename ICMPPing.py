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

def receiveOnePing(icmpSocket, ID, timeout, send_time):
	'''
	This method is used to receive a ICMP packet

	Parameter:
		icmpSocket <class 'socket.socket'>:
		ID <class 'int'>: the identification of the packet
		timeout <class 'float'>: the timeout of the ping operation
		send_time <class 'float'>: the time of sending the icmp packet
	
	Return:
		delay <class 'float'>: the delay of the ping operation
		error_str <class 'str'>: the sescription of problem
	'''
	# Wait for the socket to receive a reply
	reply = select.select([icmpSocket],[],[],float(timeout))
	if reply[0] == []:
		return 'timeout'
	# Once received, record time of receipt, otherwise, handle a timeout
	receive_time = time.time()
	# Unpack the packet header for useful information, including the ID
	receive_packet = icmpSocket.recvfrom(1024)
	icmpHeader = receive_packet[0][20:28]
	type, code, cksum, id, seq = struct.unpack(">BBHHH", icmpHeader)
	# Check that the ID matches between the request and reply
	if handle_error(type,code) == 0 and id == ID:
		delay = receive_time - send_time
		# Return total network delay
		return delay
	elif id != ID:
		return "Mismatched package"
	else:
		error_str = handle_error(type, code)
		# Return the description of the problem
		return error_str

def sendOnePing(icmpSocket, destinationAddress, ID, seq):
	'''
	This method is used to send a ICMP packet

	Parameter:
		icmpSocket <class 'socket.socket'>: the socket of the icmp
		destinationAddress <class 'str'>: the destination of the icmp packet
		ID <class 'int'>: the identification of the packet
		seq <class 'int'>:the serial number of the packet

	Return:
		send_time <class 'float'>: the time of sending the ICMP packet
	'''
	# Build ICMP header
	type = ICMP_ECHO_REQUEST
	code = 0
	cksum = 0
	id = ID
	send_time = time.time()
	body_data = b'testtesttesttesttesttesttesttest'
	packet = struct.pack('>BBHHH32s', type, code, cksum, id, seq, body_data)
	# Checksum ICMP packet using given function
	cksum = checksum(packet)
	# Insert checksum into packet
	packet = struct.pack('>BBHHH32s',type,code,cksum,id,seq,body_data)
	# Send packet using socket
	icmpSocket.sendto(packet,(destinationAddress,80))
	# Record time of sending
	return send_time

def doOnePing(destinationAddress, timeout, seq):
	'''
	This method is used to do a ping operation

	Parameter:
		destinationAddress <class 'str'>: the destination of the ping operation
		timeout <class 'float'>: the timeout of the ping operation
		seq <class 'int'>: the serial number of the packet

	Return:
		delay <class 'float'>: the delay of the ping operation 
	'''
	# 1. Create ICMP socket
	s = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))
	# 2. Call sendOnePing function
	# sometimes the pid will be greater than 65535, and H format for packing only accept 0-65535, so I use 3 to replace it
	send_time = sendOnePing(s,destinationAddress,3,seq)
	# 3. Call receiveOnePing function
	delay = receiveOnePing(s,3,timeout,send_time)
	# 4. Close ICMP socket
	s.close()
	if type(delay) == type('a'):
		return delay
	# 5. Return total network delay
	if delay>float(timeout):
		return 'timeout'
	else:
		return delay

def ping(*arg):
	'''
	The method is used to ping

	Parameter:
		arg[0] <class 'str'>: the destination of the ping operation
		arg[1] <class 'float'>: the timeout of the ping operation
		arg[2] <class 'int'>: how many times the user wants to ping the destination
	
	Return:
		None
	'''
	# the hint output
	print("now we are pinging [{}], by a 32 bytes data".format(arg[0][0]))
	# the statistics of the delays
	delay_list = []
	for i in range(int(arg[0][2])):
		# Call doOnePing function, approximately every second
		time.sleep(1)
		delay = doOnePing(arg[0][0], arg[0][1], i)
		# if the receive packet is not timeout, then add the delay to the delay_list and print it
		if type(delay) != type('a'):
			delay_list.append(delay)
			# transfer the delay to the int type and print out the returned delay
			print("Responses from {}: bytes=32 delay={}ms".format(arg[0][0],int(delay*1000//1)))
		# if the receive packet is timeout,then print timeout
		else:
			print(delay)
	# if there are some packet which are not timeout, then calculate the max, min, ave timeout the these packets.
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
