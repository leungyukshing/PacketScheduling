import socket
import sys
import time

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
	print 'Failed to create socket'
	sys.exit()
 
host = 'localhost'
port = 8888
packet_count = [100, 1000, 500]
packet_interval = [0.200, 0.25, 0.300]
packet_size = [100, 50, 100]
i = int(sys.argv[1])
for j in xrange(packet_count[i]):
	try:
		msg = str(i) + ';vishalisalltimethope' + str(j + 1)
		s.sendto(msg, (host, port))
	except socket.error, msg:
		print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	time.sleep(packet_interval[i])