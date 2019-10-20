#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import *
import sys


def handleRequest(tcpSocket):
	# 1. Receive request message from the client on connection socket
	conn, address = tcpSocket.accept()
	# 2. Extract the path of the requested object from the message (second part of the HTTP header)
	data = conn.recv(1024)
	data = data.decode().split('\n')
	filePath = data[0].split(' ')[1][1:]

	# 3. Read the corresponding file from disk
	f = open(filePath,'r')
	# 4. Store in temporary buffer
	buffer = f.read()
	# 5. Send the correct HTTP response error
	print(buffer)
	# 6. Send the content of the file to the socket
	conn.sendto(buffer.encode(),address)
	# 7. Close the connection socket
	conn.close()
	pass # Remove/replace when function is complete

def startServer(serverAddress, serverPort):
	# 1. Create server socket
	server = socket()
	# 2. Bind the server socket to server address and server port
	server.bind((serverAddress,serverPort))
	# 3. Continuously listen for connections to server socket
	server.listen(5)
	# 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/2/library/socket.html#socket.socket.accept)
	handleRequest(server);
	# 5. Close server socket
	server.close()
	pass # Remove/replace when function is complete


startServer("127.0.0.1", 8000)
