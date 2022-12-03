import socket
import sys

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
	print('Failed to create socket')
	sys.exit()
 
host = 'localhost'
port = 8888

s.sendto(str.encode("-1;dest"), (host, port))
while True:
	try:
		d = s.recvfrom(1024)
		reply = d[0]
		addr = d[1]
		print('Server reply : ' + reply)
	except socket.error as msg:
		print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()