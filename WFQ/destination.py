import socket
import sys
import time

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
	print('Failed to create socket')
	sys.exit()
 
HOST = 'localhost'
PORT = 8888

# send to router to notify the address of myself
s.sendto(str.encode("-1;dest"), (HOST, PORT))
metrics = {0: [], 1: [], 2: []}
while True:
	try:
		d = s.recvfrom(1024)
		reply = d[0]
		addr = d[1]
		payload = reply.decode("utf-8")
		print('Server reply : ' + payload)
		if payload == "connected":
			continue
		source, data = payload.split(';')
		# calculate metrics
		_, info = data.split('$')
		print("info: {}".format(info))
		source, seq, start_time = info.split('#')
		source = int(source)
		print("receive pkg ({}, {}, {})".format(source, seq, start_time))
		cost = time.time() - float(start_time)
		metrics[source].append(cost)

		# print out result
		for source, arr in metrics.items():
			print("[METRIC] source: {}, avg: {}, max: {}".format(source, 0 if len(arr) == 0 else sum(arr) / len(arr), 0 if len(arr) == 0 else max(arr)))
		
	except socket.error as msg:
		print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()