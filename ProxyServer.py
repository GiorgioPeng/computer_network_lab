# coding: utf-8
from socket import *
import sys
import re


def reRequst(proxy_socket):
    '''
    This method is used to receive local request

    Parameter:
        proxy_socket <class 'socket.socket'>: the proxy socket

    Return:
        tempSocket <class 'socket.socket'>: the socket which is used to communicate with local client
        local_address <class 'tuple'>: the address of the local client
        [ip_address, dest_port_number] <class 'list'>: the ip address and the portNumber of the destination of the remote server
        data <class 'bytes'>: the data from the local client
    '''
    # wait for the local client establish connection
    tempSocket, local_address = proxy_socket.accept()
    # receive the data which is from the local client
    data = tempSocket.recv(1048576)
    ip_address = ''
    domain = ''
    temp_data = data.decode()   # decode the data to find the destination ip address
    dest_port_number = re.findall(":\d+", temp_data.split('\n')[0])
    # it is acceptable method
    if temp_data[0:3] == 'GET' or temp_data[0:3] == 'PUT' or temp_data[0:6] == 'DELETE' or temp_data[0:4] == 'POST' or temp_data[0:4] == 'HEAD' or temp_data[0:5] == 'PATCH':
        # match the domian(this last character is \r, so use [0:-1])
        domain = re.findall(r'Host\:.*', temp_data)[0].split(' ')[1][0:-1]
        try:
            # get the ip address
            domain = domain.split(':')[0]
            ip_address = gethostbyname(domain)
        except ValueError as va:
            ip_address = gethostbyname(domain)
        except gaierror as ge:
            pass
    # the defualt port number is 80
    if dest_port_number == []:
        return [tempSocket, local_address, [ip_address, 80], data]
    else:
        dest_port_number = dest_port_number[0][1:]
        return [tempSocket, local_address, [ip_address, dest_port_number], data]


def seRequst(ip_address, data):
    '''
    This method is used to send the local client request data to the remote server

    Parameter:
        ip_address <class 'list'>: the ip address and the port number of the destination of the remote server
        data <class 'bytes'>: the data from the local client

    Return:
        send_remote_socket <class 'socket.socket'>: the socket which is used to communicate with the remote server
        'error' <class 'str'>: WinError 10061, so we should do another connect
    '''
    # create a socket which is used to communicate with the remote server
    send_remote_socket = socket()
    # ensure we can connect to the remote server
    while True:
        try:
            # connect to the remote server
            print(ip_address)
            send_remote_socket.connect((ip_address[0], int(ip_address[1])))
            break
        except TimeoutError as te:
            pass
        except ConnectionRefusedError as cre:
            print(cre)
            return 'error'
    # send the data which comes from the local client to the remote server
    send_remote_socket.sendall(data)
    return send_remote_socket


def reRespond(send_remote_socket):
    '''
    This method is used to reveive the respond packet from the remote server

    Parameter:
        send_remote_socket <class 'socket.socket'>: the socket which is used to communicate with the remote server

    Return:
        message <class 'bytes'>: the receive data from the remote server
    '''
    # receive the data from the remote server
    message = send_remote_socket.recv(1048576)
    # close the socket which is used to communicate with the remote server
    send_remote_socket.close()
    return message


def seRespond(message, data_socket):
    '''
    This method is used to send the respond data from the remote server to the local client

    Parameter:
        message <class 'bytes'>: the receive data from the remote server
        data_socket <class 'socket.socket'>: the socket which is used to communicate with local client

    Return:
        None
    '''
    try:
        # send the data to the local client
        data_socket.sendall(message)
    except ConnectionAbortedError as cae:
        # the socket is closed by something, so we do not need to close the data_socket
        print('-----------------ConnectionAbortedError-------------------')
        return 'ConnectionAbortedError'
    # close the socket which is used to communicate with local client
    data_socket.close()
    return


if __name__ == "__main__":
    port_number = input("please input the port number of you proxy:\n")
    port_number = int(port_number)
    # ensure the user input a right port number
    while port_number > 65535 or port_number < 0:
        port_number = input('Please input the right port number: \n')
        port_number = int(port_number)
    # create the proxy socket
    proxy_socket = socket()
    proxy_socket.bind(('127.0.0.1', port_number))
    proxy_socket.listen(5)
    # proxy_socket.setblocking(1) # set the socket in block mode

    while True:
        # get some data from local client
        data_socket, local_address, ip_address, data = reRequst(proxy_socket)
        # if its method is https or options
        if ip_address[0] == '':
            continue
        # send the data to the remote server
        send_remote_socket = seRequst(ip_address, data)
        # if WinError 10061 occur, we should do another connect
        if send_remote_socket == 'error':
            continue
        # get respond from the remote server
        message = reRespond(send_remote_socket)
        # send respond data to the local client
        seRespond(message, data_socket)

    # close the proxy socket
    proxy_socket.close()
