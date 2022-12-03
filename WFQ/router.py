import socket
import sys
import time
import threading

HOST = '127.0.0.1'
PORT = 8888

INT_MAX = 999999999999999

current_milli_time = lambda: int(round(time.time() * 1000))

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
destination_address = None
round_number = 0 # like real time?
source = {0:{'time':[],'data':[], 'fno':[], 'active':0, 'sent':[0]}, 1:{'time':[], 'data':[], 'fno':[], 'active':0, 'sent':[0]}, 2:{'time':[], 'data':[], 'fno':[], 'active':0, 'sent':[0]}}
packet_size = [100, 50, 100] # maybe we should read from the input?
numpackets = [2, 4, 1] # weights
sleeptime = [0.1, 0.05, 0.1]
global_start_time = None # record the first packet arrival time
flag = 0 # used to initialize states
rDash = 0 # rate for 

# activeConn = 0 # UNUSED
# iters = {0:0, 1:0, 2:0} # UNUSED
# count = 0 # UNUSED

def recvpacket():
	global source
	global flag
	global rDash
	while True:
		d = s.recvfrom(1024)
		recv_time = current_milli_time()
		d_decoded = d[0].decode()
		sourcey, data = d_decoded.split(';')
		sourcey = int(sourcey)
		print(data)
		if data == "dest":
			global destination_address
			destination_address = d[1]
			s.sendto(str.encode("connected"), destination_address)
			continue
		if flag == 0:
			prev_time = 0 # arrival time for the previous packet (relative to global)
			global_start_time = recv_time
			round_number = 0
			flag = 1 # initialized
		if len(source[sourcey]['fno']) == 0:
			print('First packet')
			fno = round_number + (packet_size[sourcey] * 1.0 / numpackets[sourcey])
			source[sourcey]['fno'].append(fno)
		else:
			print('length', len(source[sourcey]['fno']), 'source', sourcey)
			fno = max(round_number, source[sourcey]['fno'][len(source[sourcey]['fno']) - 1]) + (packet_size[sourcey] * 1.0 / numpackets[sourcey])
			source[sourcey]['fno'].append(fno)
		source[sourcey]['time'].append(recv_time - global_start_time)
		source[sourcey]['data'].append(str(sourcey) + ';' + data)
		source[sourcey]['sent'].append(0)
		round_number += ((recv_time - global_start_time) - prev_time)*rDash
		lFno = max(source[sourcey]['fno'])
		print(lFno, round_number)
		if lFno > round_number:
			source[sourcey]['active'] = 1
		else:
			source[sourcey]['active'] = 0
		weightsSum = 0
		for i in range(3):
			if source[i]['active'] == 1:
				weightsSum += numpackets[i]
		if weightsSum == 0:
			continue
		rDash = 1.0 / weightsSum
		prev_time = recv_time - global_start_time
	# s.close() # code unreachable

def sendpacket():
	while True:
		if destination_address:
			mini = INT_MAX
			index = 0
			so = 0
			for i in range(3):
				for j in range(len(source[i]['fno'])):
					if source[i]['sent'][j] == 0:
						if source[i]['fno'][j] < mini:
							mini = min(source[i]['fno'])
							index = j
							so = i
			if mini != INT_MAX:
				s.sendto(str.encode(source[so]['data'][index]), destination_address)
			source[so]['sent'][index] = 1
			time.sleep(sleeptime[so])

t1 = threading.Thread(target=recvpacket)
t1.daemon = True
t2 = threading.Thread(target=sendpacket)
t2.daemon = True

t1.start()
t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)