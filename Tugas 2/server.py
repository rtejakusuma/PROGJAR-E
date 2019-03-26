from threading import Thread
import socket
import os
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000

BUFSIZE = 1024

imgpath ="./image/"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

def getRequest():
    while True:
        print "Waiting Request"
        data, addr = sock.recvfrom(1024)
        data_to_string = str(data)
        print "Client : " + str(data)
        if data_to_string[:3] == "RDY":
            thread = Thread(target=setImage, args=(addr))
            thread.start()

       
def setImage(ip, port):
    addr = (ip, port)
    ImageName = ["hibiki1.jpg","hibiki2.jpg","hibiki3.jpg"]
    for x in ImageName:
        sendImg(x,addr)
    sock.sendto("CLOSE".ljust(1024), addr)

def sendImg(imgname, addr):
    completeName = os.path.join(imgpath, imgname)
    fp = open(completeName, "rb")
    pckg = fp.read()
    sizeSent = 0
    fp.close()
    sock.sendto(("START " + imgname).ljust(1024), addr)
    iterate=(len(pckg)/BUFSIZE)
    for i in range(iterate + 1):
        data = []
        if (i+1)*BUFSIZE > len(pckg):
            data = pckg[i*BUFSIZE:len(pckg)]
            sizeSent += len(data)
            data.ljust(1024)
        else:
            data = pckg[i*BUFSIZE:(i+1)*BUFSIZE]
            sizeSent += len(data)
        sock.sendto(data, addr)
        print "Sending "+str(sizeSent) + " of " + str(len(pckg)) + " bytes"
    sock.sendto(("END " + imgname).ljust(1024), addr)
    

while True:
    getRequest()