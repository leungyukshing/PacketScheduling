import socket
import sys
import time
import threading
import collections

HOST = '127.0.0.1'
PORT = 8888

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')
except socket.error as msg:
    print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')
daddr = None
source = {0: [], 1: [], 2: []}
# source = {}
for i in range(3):
    source[i] = collections.deque()
packet_size = [100, 50, 100]
count = 0
numpackets = [2, 4, 1]
sleeptime = [0.1, 0.05, 0.1]
daddr = None
quantum_size = 30
deficit = [0, 0, 0]


def recvpacket():
    while True:
        d = s.recvfrom(1024)
        d_decoded = d[0].decode()
        sourcey, data = d_decoded.split(';')
        print(data)
        if data == "dest":
            global daddr
            daddr = d[1]
            s.sendto(str.encode("connected"), daddr)
        else:
            global source
            print('debug', sourcey)
            print('length', len(source[int(sourcey)]), 'source', sourcey)
            source[int(sourcey)].append(sourcey + ';' + data)
    # s.close()


def sendpacket():
    while True:
        if daddr:
            for j in range(3):
                deficit[j] += quantum_size
                if len(source[j]) != 0 and deficit[j] >= packet_size[j]:
                    deficit[j] -= packet_size[j]
                    s.sendto(str.encode(source[j].popleft()), daddr)
                    time.sleep(sleeptime[j])


t1 = threading.Thread(target=recvpacket)
t2 = threading.Thread(target=sendpacket)
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)