#  coding: utf-8 
import socketserver
import os
import sys
from mimetypes import guess_type
from pathlib import Path
# https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        try:
            decodedData=self.data.decode("utf-8")
            linesOfRequest=decodedData.split("\r\n")
            firstLineOfReq=linesOfRequest[0].split()
            requestType=firstLineOfReq[0]
            requestFile=firstLineOfReq[1]
            if requestType != "GET":
                self.request.sendall("HTTP/1.1 405 Not Allowed\r\n\r\n".encode())
                self.request.sendall("405 Not Allowed".encode())
                return
            if requestFile[:3] == '/..':
                self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                self.request.sendall("404 Not Found".encode())
                return
            if requestFile[-1] == '/':
                requestFile += "index.html"
            #print(requestFile)
            pth=os.path.abspath("www"+requestFile)
            #print(pth)
            if not os.path.isfile(pth) and not os.path.isdir(pth):
                self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                self.request.sendall("404 Not Found".encode())
                return
            if os.path.isdir(pth):
                self.request.sendall("HTTP/1.1 301 Permanently Moved\r\n\r\n".encode())
                loc="Location: "+"http://127.0.0.1/www"+requestFile+'/'
                self.request.sendall(loc.encode())
                return
            file=open("www"+requestFile,'r')
            responseTxt=""
            for line in file:
                responseTxt += line
            self.request.sendall("HTTP/1.1 200 OK\r\n".encode())
            fileType,encoding=guess_type(requestFile)
            contentTypeString="Content-Type: "+str(fileType)+"; charset=UTF-8\r\n"
            contentLengthString="Content-Length: "+str(len(responseTxt))+'\r\n'
            connectionCloseString='Connection: close' + "\r\n\r\n"
            responseTxtString=responseTxt+"\r\n"
            self.request.sendall(contentTypeString.encode())
            self.request.sendall(contentLengthString.encode())
            self.request.sendall(connectionCloseString.encode())
            self.request.sendall(responseTxtString.encode())
            file.close()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.request.sendall("HTTP/1.1 404 Not Found \r\n\r\n".encode())
            self.request.sendall("404 Not Found".encode())
        finally:
            self.request.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
