#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import *
import sys


def handleRequest(tcpSocket):
	# 1. Receive request message from the client on connection socket
	while True:
		conn, address = tcpSocket.accept()
		# 2. Extract the path of the requested object from the message (second part of the HTTP header)
		data = conn.recv(1024)
		print(data.decode())
		data = data.decode().split('\n')
		try:
			filePath = data[0].split(' ')[1][1:]
			# if filePath == 'favicon.ico':
			# 	continue
			if filePath == '':
				filePath = 'index.html'
		except IndexError as e:
			pass

		try:
			# 3. Read the corresponding file from disk
			f = open(filePath,'rb')
			# 4. Store in temporary buffer
			buffer = f.read()
			# 5. Send the correct HTTP response error
			conn.sendall(bytes('HTTP/1.1 200 OK\r\n\r\n', 'utf8'))
			# 6. Send the content of the file to the socket
			conn.sendall(buffer)
			# 7. Close the connection socket
		except FileNotFoundError as fe:
			f = open('404.html','rb')
			buffer = f.read()
			conn.sendall(bytes('HTTP/1.1 404 Not Found\r\n\r\n','utf8'))
			conn.sendall(buffer)

		conn.close()
	pass # Remove/replace when function is complete

def startServer(serverAddress, serverPort):
	# 1. Create server socket
	server = socket()
	# 2. Bind the server socket to server address and server port
	server.bind((serverAddress,serverPort))
	# 3. Continuously listen for connections to server socket
	server.listen(1)
	# 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/2/library/socket.html#socket.socket.accept)
	handleRequest(server)
	# 5. Close server socket
	server.close()
	pass # Remove/replace when function is complete

if __name__ == "__main__":
	port_number = input("Please input the port number:\n")
	try:
		port_number = int(port_number)
		if port_number < 65536 and port_number > 0:
			startServer("127.0.0.1",port_number)
		else:
			startServer("127.0.0.1", 8000)
	except ValueError as ve:
		startServer("127.0.0.1", 8000)