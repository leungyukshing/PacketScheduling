import socket
import sys
import time
import threading
HOST = '127.0.0.1'
PORT = 8888

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print 'Socket created'
except socket.error, msg:
	print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
	 
print 'Socket bind complete'
daddr = None
source = {0:[], 1:[], 2:[]}
packet_size = [100, 50, 100]
iters = {0:0, 1:0, 2:0}
count = 0
numpackets=[2,8,1]
sleeptime=[0.1,0.05,0.1]
daddr=None
def recvpacket():
	while True:
		d = s.recvfrom(1024)
		sourcey, data = d[0].split(';')
		print data
		if data == "dest":
			global daddr
			daddr= d[1]
			s.sendto("connected", daddr)
		else:
			global source
			source[int(sourcey)].append(sourcey + ';' + data)
	s.close()

def sendpacket():
#	num = [0, 0, 0]
	while True:
		if daddr:
			for j in range(3):
				for i in range(numpackets[j]):
					if len(source[j])==0:
						continue
					else:
						s.sendto(source[j][0],daddr)
						num[j] += 1
						del source[j][0]
						time.sleep(sleeptime[j])
#			print num


t1 = threading.Thread(target=recvpacket)
t2 = threading.Thread(target=sendpacket)
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)