#!/usr/bin/python
# -*- coding: UTF-8 -*-

from socket import *
import sys
import _thread


def handleRequest(thread_name, conn, address):
    '''
    This method is used to deal with message communication between the server and the client

    Parameter:
        tcpSocket <class 'socket.socket'>: the socket of the server

    Return:
        None

    '''
    # 1. Receive request message from the client on connection socket
    data = conn.recv(1024)
    # 2. Extract the path of the requested object from the message (second part of the HTTP header)
    # print(data.decode())
    data = data.decode().split('\n')
    try:
        # get the path of the file
        filePath = data[0].split(' ')[1][1:]
        # if the path is null, send the index.html to the user
        if filePath == '':
            filePath = 'index.html'
    except IndexError as e:
        filePath = 'index.html'

    try:
        # 3. Read the corresponding file from disk
        f = open(filePath, 'rb')
        # 4. Store in temporary buffer
        buffer = f.read()
        # 5. Send the correct HTTP response
        conn.sendall(bytes('HTTP/1.1 200 OK\r\n\r\n', 'utf8'))
        # 6. Send the content of the file to the socket
        conn.sendall(buffer)
    except FileNotFoundError as fe:
        f = open('404.html', 'rb')
        buffer = f.read()
        try:
            # 5. Send the correct HTTP response
            conn.sendall(bytes('HTTP/1.1 404 Not Found\r\n\r\n', 'utf8'))
            # 6. Send the content of the file to the socket
            conn.sendall(buffer)
        # if the connection is closed by something, we do the same things again
        except ConnectionAbortedError as cae:
            print(ConnectionAbortedError)
            return
    # if the connection is closed by something, we do the same things again
    except ConnectionAbortedError as car:
        print(ConnectionAbortedError)
        return

    # 7. Close the connection socket
    conn.close()
    return


def startServer(serverAddress, serverPort):
    '''
    This method is used to start the server

    Parameter:
        serverAddress <class 'str'>: the address of the server
        serverPort <class 'int'>: the port number of the server

    Return:
        None
    '''
    # 1. Create server socket
    server = socket()
    # 2. Bind the server socket to server address and server port
    server.bind((serverAddress, serverPort))
    # 3. Continuously listen for connections to server socket
    server.listen(1)
    # 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/2/library/socket.html#socket.socket.accept)
    while True:
        conn, address = server.accept()
        _thread.start_new_thread(handleRequest, ('thread', conn, address))
    # 5. Close server socket
    server.close()


if __name__ == "__main__":
    port_number = input("Please input the port number:\n")
    while True:
        try:
            port_number = int(port_number)
            if port_number < 65536 and port_number > 0:
                startServer("127.0.0.1", port_number)
                break
            else:
                # if the user inputs a wrong port number
                port_number = input("Please input the right port number:\n")
        except ValueError as ve:
            # if the user does not input a number
            port_number = input("Please input the right port number:\n")
