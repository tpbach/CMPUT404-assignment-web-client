#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split('\r\n')[0].split(" ")[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def GET(self, url, args=None):
        parsedURL = urllib.parse.urlparse(url)
        host = parsedURL.hostname
        
        # Get port, otherwise set to default 80
        if parsedURL.port:
            port = parsedURL.port
        else:
            port = 80

        # Get path, otherwise set to default '/'
        if parsedURL.path:
            path = parsedURL.path
        else:
            path = "/"
        self.connect(host, port)

        getRequest= (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Accept: */*\r\n"
            f"Connection: close\r\n\r\n"
        )

        self.print_output("GET", getRequest)

        self.sendall(getRequest)
        response = str(self.recvall(self.socket))

        self.print_output("", response)

        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsedURL = urllib.parse.urlparse(url)
        host = parsedURL.hostname
        
        # Get port, otherwise set to default 80
        if parsedURL.port:
            port = parsedURL.port
        else:
            port = 80
        self.connect(host, port)

        # Get path, otherwise set to default '/'
        if parsedURL.path:
            path = parsedURL.path
        else:
            path = "/"
        
        # Format arguments with & in between
        # Inspiration taken from CB Bailey
        # https://stackoverflow.com/a/7277102
        if args:
            postBody = "&".join(f"{i}={j}" for i, j in args.items())
        else:
            postBody = ""

        contentLength = len(postBody.encode())

        postRequest = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {contentLength}\r\n"
            f"Connection: close\r\n\r\n"
            f"{postBody}"
        )
        
        self.print_output("POST", postRequest)
        
        self.sendall(postRequest)
        response = self.recvall(self.socket)

        self.print_output("", response)

        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    
    def print_output(self, type, data):
        if type == "GET":
            header = "\n----------------- GET REQUEST -----------------\n"
        elif type == "POST":
            header = "\n----------------- POST REQUEST -----------------\n"
        else:
            header = "\n----------------- RESPONSE -----------------\n"

        footer = "\n" + "-"*len(header) + "\n"
        outputString = header + data + footer
        print(outputString)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
