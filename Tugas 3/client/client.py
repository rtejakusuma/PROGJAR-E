import socket
import threading
import os

SERVER_PORT = 10000
SERVER_IP = "127.0.0.1"
BLOCK_SIZE = 1024

class ClientConnection:
    def __init__(self, conn):
        print "\nCommand"
        print "ls \t cd [...] \t upload [...] \t download [...]\n"
        self.conn = conn
        connInfo = conn.getsockname()
    def run(self):
        while True:
            request = sock.recv(BLOCK_SIZE).rstrip()
            print request,
            if request[:5] == "READY":
                cmd = raw_input()
                self.parseRequest(cmd)
            
    def parseRequest(self, request):
        if request[:2] == "cd":
            self.send("CHDIR " + request[3:])
            print self.recv().rstrip()
        elif request[:3] == "ls":
            self.send("LIST")
            print self.recv().rstrip()
        elif request[:6] == "upload":
            self.sendFile(request[7:])
        elif request[:8] == "download":
            self.recvFile(request[9:])
        else:
            self.send("$")
            print self.recv().rstrip()

    def sendFile(self, name):
        fp = None
        try:
            fp = open(name, "rb")
        except:
            print "FILE NOT FOUND"
            return
        payload = fp.read()
        sentSize = 0
        addr = self.conn.getsockname()
        fp.close()
        self.send("UPLOAD "+name)
        signal = self.recv()
        if signal[:2] != "OK":
            print "Invalid response"
            return
        for i in range((len(payload)/BLOCK_SIZE) + 1):
            data = []
            if (i+1)*BLOCK_SIZE > len(payload):
                data = payload[i*BLOCK_SIZE:len(payload)]
                sentSize += len(data)
                data.ljust(1024)
            else:
                data = payload[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE]
                sentSize += len(data)
            self.send(data)
            print "Sending "+str(sentSize) + " OF " + str(len(payload)) + " To " + str(addr[0]) + ":" + str(addr[1])
        self.send("END")

    def send(self, payload):
        self.conn.send(payload.ljust(BLOCK_SIZE))

    def recvFile(self, fileName):
        self.send("DOWNLOAD " + fileName)
        ok = self.recv()
        if ok[:2] != "OK":
            print "Invalid response : " + ok
            return
        self.send("OK")
        fp = open(fileName, "wb+")
        received = 0
        while True:
            data = self.recv()
            if data[:3] == "END":
                fp.close()
                print "End Send " + fileName
                break
            else:
                fp.write(data) 
                received += len(data)
                print "Received "+ str(received)
       
    def recv(self):
        return self.conn.recv(BLOCK_SIZE)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP,SERVER_PORT))

conn = ClientConnection(sock)
conn.run()