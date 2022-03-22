#!/usr/bin/env python3

import socket
import sys
import os
import select
import queue

from file_reader import FileReader


class Jewel:

    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.bind(("networks-da7nav.herokuapp.com", port))
        server.listen(50)
        inputs = [server]
        outputs = []
        message_queues = {}

        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)

            for s in readable:
                if s is server:
                    (client, address) = s.accept()
                    client.setblocking(0)
                    inputs.append(client)
                    message_queues[client] = queue.Queue()
                    print(f"[CONN] Connection from {address[0]} on port {address[1]}")
                else:
                    data = s.recv(1024)
                    if data:
                        message_queues[s].put(data)
                        if s not in outputs:
                            outputs.append(s)
                    else: 
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del message_queues[s]

            for s in writable:
                try:
                    data = message_queues[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    IncomingData = Pars()
                    lines = IncomingData.pars_data(data.decode('utf-8'))
                    request_fields = lines[0].split()
                    headers = lines[1:]
                    if (request_fields[0] == 'GET'):
                        print(f"[REQU] [{address[0]}:{address[1]}] GET request for {request_fields[1]}")
                        typeFile = ""
                        if '.html' in request_fields[1]:
                            typeFile = "text/html"
                        elif '.css' in request_fields[1]:
                            typeFile = "text/css"
                        elif '.png' in request_fields[1]:
                            typeFile = "image/png"
                        elif '.jpg' in request_fields[1]:
                            typeFile = "image/jpeg"
                        elif '.gif' in request_fields[1]:
                            typeFile = "image/gif"
                        else:
                            typeFile = "/"
                        if typeFile != "/":
                            cookies = (headers[-1].split())[1]
                            message = file_reader.get(file_path + request_fields[1], cookies)
                            if message == None:
                                print(f"[ERRO] [{address[0]}:{address[1]}] GET request returned error 404")
                                s.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                            else:
                                size = (file_reader.head(file_path + request_fields[1], cookies))
                                header = (f"HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nContent-Length: {size}\r\nContent-Type: {typeFile}\r\nServer: networks-da7nav\r\n\r\n").encode()
                                #print(header)
                                s.send(header)
                                #print(message)
                                s.send(message)
                        else: 
                            cookies = (headers[-1].split())[1]
                            message = file_reader.get(file_path + request_fields[1], cookies)
                            if message == None:
                                print(f"[ERRO] [{address[0]}:{address[1]}] GET request returned error 404")
                                s.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                            else:
                                header = b'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nContent-Length: 1024\r\nContent-Type: text/html\r\n\r\n'
                                #print(header)
                                s.send(header)
                                directory = (f"<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Page Title</title>\r\n</head>\r\n<body>\r\n<h1>{request_fields[1]}</h1>\r\n</body>\r\n</html>").encode()
                                #print(directory)
                                s.send(directory)

                    elif (request_fields[0] == 'HEAD'):
                        print(f"[REQU] [{address[0]}:{address[1]}] HEAD request for {request_fields[1]}")
                        typeFile = ""
                        if '.html' in request_fields[1]:
                            typeFile = "text/html"
                        elif '.css' in request_fields[1]:
                            typeFile = "text/css"
                        elif '.png' in request_fields[1]:
                            typeFile = "image/png"
                        elif '.jpg' in request_fields[1]:
                            typeFile = "image/jpeg"
                        elif '.gif' in request_fields[1]:
                            typeFile = "image/gif"
                        else:
                            typeFile = "/"
                        if typeFile != "/":
                            cookies = (headers[-1].split())[1]
                            size = file_reader.head(file_path + request_fields[1], cookies)
                            if size == None:
                                print(f"[ERRO] [{address[0]}:{address[1]}] HEAD request returned error 404")
                                s.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                            else:
                                header = (f"HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nContent-Length: {size}\r\nContent-Type: {typeFile}\r\n\r\n").encode()
                                #print(header)
                                s.send(header)
                        else: 
                            cookies = (headers[-1].split())[1]
                            message = file_reader.head(file_path + request_fields[1], cookies)
                            if message == None:
                                print(f"[ERRO] [{address[0]}:{address[1]}] HEAD request returned error 404")
                                s.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                            else:
                                header = b'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nContent-Length: 1024\r\nContent-Type: text/html\r\n\r\n'
                                #print(header)
                                s.send(header)
                    else:
                        print(f"[ERRO] [{address[0]}:{address[1]}] request returned error 501")
                        s.send(b'HTTP/1.1 501 Not Implemented\r\nContent-Length: 0\r\n\r\n')

            for s in exceptional:
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()
                del message_queues[s]
                    #break
        server.close()

class Pars:

    def __init__(self):
        pass

    def pars_data(self, incoming):
        self.incoming = incoming

        header_end = incoming.find('\r\n\r\n')
        if header_end > -1:
            header_string = incoming[:header_end]
            lines = header_string.split('\r\n')

            request_fields = lines[0].split()
            headers = lines[1:]

            #print(request_fields)

            for header in headers:
                header_fields = header.split(':')
                key = header_fields[0].strip()
                val = header_fields[1].strip()
                #print('{}: {}'.format(key, val))

            return lines
            


if __name__ == "__main__":
    port = int(sys.argv[1])
    file_path = sys.argv[2]

    FR = FileReader()

    J = Jewel(port, file_path, FR)
