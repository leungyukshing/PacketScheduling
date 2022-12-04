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
packet_size = [30, 50, 100]
count = 0
numpackets = [2, 4, 1]
sleeptime = [0.1, 0.05, 0.1]
daddr = None
quantum_size = 30
deficit = [0, 0, 0]

# metrics variable
packet_received = 0
packet_sent = 0

# Send Rate Control

# We'll limit ourself to a 10B/sec maximum send rate
maxSendRateBytesPerSecond = 100

# We'll add to this tally as we send() bytes, and subtract from
# at the schedule specified by (maxSendRateBytesPerSecond)
bytesAheadOfSchedule = 0

prev_send_time = None

def ConvertSecondsToBytes(numSeconds):
   return numSeconds*maxSendRateBytesPerSecond

def ConvertBytesToSeconds(numBytes):
   return float(numBytes)/maxSendRateBytesPerSecond


def recvpacket():
    global packet_received
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
            packet_received += 1
            print('debug', sourcey)
            print('length', len(source[int(sourcey)]), 'source', sourcey)
            source[int(sourcey)].append(sourcey + ';' + data)
    # s.close()


def sendpacket():
    global packet_sent
    global prev_send_time
    global bytesAheadOfSchedule
    while True:
        if daddr:
            for j in range(3):
                deficit[j] += quantum_size
                if len(source[j]) != 0 and deficit[j] >= packet_size[j]:
                    deficit[j] -= packet_size[j]
                    now = time.time()
                    if prev_send_time != None:
                        bytesAheadOfSchedule -= ConvertSecondsToBytes(now - prev_send_time)
                    prev_send_time = now

                    numBytesSent = s.sendto(str.encode(source[j].popleft()), daddr)
                    if (numBytesSent > 0):
                        bytesAheadOfSchedule += numBytesSent
                        if (bytesAheadOfSchedule > 0):
                            print("router sleep {}".format(bytesAheadOfSchedule))
                            time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule))
                    else:
                        print("Error sending data, exiting!")
                        break
                    print("router send packet done. packet_received: {}, packet_send: {}".format(packet_received, packet_sent))
                    packet_sent += 1
                    # time.sleep(sleeptime[j])

def getmetrics():
	global packet_received
	global packet_sent
	total_throughput = 0.0
	total = 0
	while True:
		# log every 500 ms
		if packet_received == 1600:
			break
		throughput = 0 if packet_received == 0 else packet_sent / packet_received
		if throughput > 0:
			total += 1
			total_throughput += throughput

		print("[STAT] packet_received: {}, packet_sent: {}, throughput(sent/received): {}, avg_throughput: {}".format(packet_received, packet_sent, throughput, 0 if total == 0 else total_throughput / total))
		time.sleep(0.5)


t1 = threading.Thread(target=recvpacket)
t2 = threading.Thread(target=sendpacket)
t3 = threading.Thread(target=getmetrics)
t1.daemon = True
t2.daemon = True
t3.daemon = True


t1.start()
t2.start()
t3.start()

while threading.active_count() > 0:
    time.sleep(0.1)