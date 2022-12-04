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

# Send Rate Control
# We'll limit ourself to a 10B/sec maximum send rate
maxSendRateBytesPerSecond = 30

def ConvertSecondsToBytes(numSeconds):
   return numSeconds * maxSendRateBytesPerSecond

def ConvertBytesToSeconds(numBytes):
   return float(numBytes) / maxSendRateBytesPerSecond

# We'll add to this tally as we send() bytes, and subtract from
# at the schedule specified by (maxSendRateBytesPerSecond)
bytesAheadOfSchedule = 0

prev_send_time = None

packet_count = [300, 300, 300]
packet_interval = [0.200, 0.25, 0.300]
packet_size = [30, 50, 100]
source_id = int(sys.argv[1])
for j in range(packet_count[source_id]):
	try:
		now = time.time()
		msg = str(source_id) + ';xcdisshabi$' + str(source_id) + "#" + str(j + 1) + "#" + str(now)
		if (prev_send_time != None):
			bytesAheadOfSchedule -= ConvertSecondsToBytes(now - prev_send_time)
		prev_send_time = now
		numBytesSent = s.sendto(str.encode(msg), (HOST, PORT))
		if (numBytesSent > 0):
			bytesAheadOfSchedule += numBytesSent
			if (bytesAheadOfSchedule > 0):
				time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule))
		else:
			print("Error sending data, exiting!")
			break
	except socket.error as msg:
		print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
	# time.sleep(packet_interval[source_id])