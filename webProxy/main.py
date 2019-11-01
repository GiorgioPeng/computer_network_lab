# coding: utf-8
from socket import *
import sys
import re

def reRequst(proxy_socket):
    tempSocket, local_address = proxy_socket.accept()
    data = tempSocket.recv(1024)
    ip_address = ''
    temp_data = data.decode()   # decode the data to find the destination ip address
    print(temp_data)
    if temp_data[0:3] == 'GET':  # if is GET method, because HTTPS is connect
            domain = re.findall(r'\/{1}[^/]+?\/', temp_data)  # match the domian
            try: 
                ip_address = gethostbyname(domain[0][1:-1]) # get the ip address
            except gaierror as ge:
                pass

            # print(ip_address)
    return [tempSocket,local_address,ip_address,data]

def seRequst(ip_address,data):
    send_remote_socket = socket()
    send_remote_socket.connect((ip_address,80))
    send_remote_socket.sendall(data)
    return send_remote_socket

def reRespond(send_remote_socket):
    message = send_remote_socket.recv(65536) # receive the data from the remote server
    send_remote_socket.close()
    # message = gzip.decompress(message).decode("utf-8")
    return message

def seRespond(message,data_socket):
    data_socket.sendall(message)
    data_socket.close()
    return 

if __name__ == "__main__":
    port_number = input("please input the port number of you proxy:\n")
    port_number = int(port_number)
    proxy_socket = socket()
    proxy_socket.bind(('127.0.0.1',port_number))
    proxy_socket.listen(1)
    # proxy_socket.setblocking(1) # set the socket in block mode

    while True:
        data_socket, local_address, ip_address, data = reRequst(proxy_socket)
        if ip_address == '':
            continue
        send_remote_socket = seRequst(ip_address,data)
        message = reRespond(send_remote_socket) # get responde from the remote server
        seRespond(message, data_socket)
        
    proxy_socket.close()
