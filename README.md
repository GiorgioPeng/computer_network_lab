# This one include some experiments, icmp, traceroute, webserver, webproxy, of the computer network lecture.

---  

## icmp:

#### how to use?

```
python ICMPPing.py [the ip or domain name of the destination] [timeout] [times]

```

#### result?

- the ip of the destination
- packet length and the delay of each ping
- the maximum delay, minimum delay, average delay

---  

## traceroute:

#### how to use?

> please close the firewall, because the firewall will drop the useless packets, which is returned by ttl equal 0 or other bad reasons.

```
python Traceroute.py
```

1. input the destination

2. input the timeout

#### result?

- the ip of the destination
- the information which include the index, the reasons of packet returned, the delay, the ip or domain name of the destination (* represents lost or timed packets)

---  

## webserver:

> you can input _localhost:xxxx/filePathOfTheWebsite_ or  _127.0.0.1:xxxx/filePathOfTheWebsite_  in the Browser address bar

> the __'xxxx'__ is the port number of the webserver, the __'filePathOfTheWebsite'__ is the path of your website file

> if you do not input any path, the browser will open the __'index.html'__ file.

> if you input a nonexistent path, the browser will open the __'404.html'__ file.

#### how to use?

```
python WebServer

```
1. input the port number of the web server

#### result?

- the information of the request packet will be printed in the commond line

---  

## webclient

> this one only can connect to the 8000 port, if you need to connect to other port number, please modify this one.

> the webclient will request a website from the webserver about every 2 seconds.

#### how to use?

```
python WebClient.py
```

#### result?

- the content of the returned file from the webserver

---  

## webproxy:

> set you proxy address(127.0.0.1) and the proxy port number

> use browser to visit some website

> this script does not support __https__, but it can use in __put__, __get__, __put__, __patch__ and __delete__ request

> if you want to access your local server using a proxy, use your IP instead of localhost or 127.0.0.1

#### how to use?

```
python ProxyServer.py
```

1. input the port number of you proxy server

#### result?

- lists which include a ip address and the port number of the destination

#### 
