import socket
import sys

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

HOST = 'localhost'
PORT = 8888

# send to router to notify the address of myself
s.sendto(str.encode("-1;dest"), (HOST, PORT))

while True:
    try:
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]
        print('Server reply : ' + str(reply))
    except socket.error as msg:
        print('Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()