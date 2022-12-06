import socket
import sys
import time
import threading
from collections import deque

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
round_number = 0
packet_size = [30, 50, 100]  # maybe we should read from the input?
numpackets = [2, 4, 1]  # weights
sleeptime = [0.1, 0.05, 0.1]


# metrics variable
packet_received = 0
packet_sent = 0


# activeConn = 0 # UNUSED
# iters = {0:0, 1:0, 2:0} # UNUSED
# count = 0 # UNUSED

# Send Rate Control

# We'll limit ourself to a 60B/sec maximum send rate
maxSendRateBytesPerSecond = 60

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
            global destination_address
            destination_address = d[1]
            s.sendto(str.encode("connected"), destination_address)
        else:
            global source
            packet_received += 1
            print('length:', len(leaf_list[int(sourcey)].real_queue), 'source:', sourcey)
            arrive(int(sourcey), (sourcey, data))
    # s.close()


# Hierarchical Packet Fair Queueing Algorithms
# real queue of flow i 

#              (link)root(pfq) 
#                /         \
#        node0(pfq)        node1(pfq)
#         /     \             /
#  leaf(flow0) leaf(flow1) leaf(flow2)
class Node:
    def __init__(self, left, right, logic_queue, parent, weight=0, s=0, f=0 ,Vt=0, Busy=False, activeChild=None):
        self.left = left
        self.right = right
        self.logic_queue = logic_queue
        self.parent = parent
        self.weight = weight
        self.s = s
        self.f = f
        self.Vt = Vt
        self.Busy = Busy
        self.activeChild = activeChild

class leafNode:
    def __init__(self, real_queue, logic_queue, parent, weight=1, s=0, f=0 ,Vt=0):
        self.real_queue = real_queue
        self.logic_queue = logic_queue
        self.parent = parent
        self.weight = weight
        self.s = s
        self.f = f
        self.Vt = Vt


# implement tree
dummy_root = Node(left=None, right=None, logic_queue=deque(), parent=None)
tree_root = Node(left=None, right=None, logic_queue=deque(), parent=dummy_root)
node0 =  Node(None, None, deque(), tree_root)
node1 = Node(None, None, deque(), tree_root)


leaf0 = leafNode(real_queue=deque(), logic_queue=deque(), parent=node0, weight=2)
leaf1 = leafNode(real_queue=deque(), logic_queue=deque(), parent=node0, weight=4)
leaf2 = leafNode(real_queue=deque(), logic_queue=deque(), parent=node1, weight=1)
node0.left = leaf0
node0.right = leaf1
node1.left = leaf2
tree_root.left = node0
tree_root.right = node1
dummy_root.left = tree_root
leaf_list = [leaf0, leaf1, leaf2]


def reset_path(node: Node):
    # some comment
    node.logic_queue.popleft()
    if isinstance(node, leafNode):
        node.real_queue.popleft()
        if len(node.real_queue) != 0:
            node.logic_queue.append(node.real_queue[0])
            node.s = node.f
            node.f = node.s + (len(node.logic_queue[0])*1.0 / node.weight) # rn = weight
        restart_node(node.parent)
    else:
        m = node.activeChild
        node.activeChild = None
        node.weight = 0
        reset_path(m)


def transmit_packet_to_link(node):
    global prev_send_time
    global bytesAheadOfSchedule
    global packet_sent
    # set Vt of dummy root
    node.parent.Vt = node.f
    id, data = node.logic_queue[0]

    now = time.time()
    if prev_send_time != None:
        bytesAheadOfSchedule -= ConvertSecondsToBytes(now - prev_send_time)
    prev_send_time = now

    numBytesSent = s.sendto(str.encode(str(id) + ";" + data), destination_address)
    reset_path(node)
    if (numBytesSent > 0):
        bytesAheadOfSchedule += numBytesSent
        if (bytesAheadOfSchedule > 0):
            print("router sleep {}".format(bytesAheadOfSchedule))
            time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule))
    else:
        print("Error sending data, exiting!")
        return
    print("router send packet done. packet_received: {}, packet_send: {}".format(packet_received, packet_sent))
    packet_sent += 1

def select_next(n: Node):
    # this only fit our three leaves nodes tree, looking forward our feature work
    if not n.right or len(n.right.logic_queue) == 0:
        return n.left
    if not n.left or len(n.left.logic_queue) == 0:
        return n.right
    if n.left.f <= n.right.f:
        return n.left
    else:
        return n.right

def restart_node(parent_node: Node):
    node_to_schedule = select_next(parent_node)
    if len(node_to_schedule.logic_queue):
        # ActiveChildn <- m
        parent_node.activeChild = node_to_schedule
        parent_node.logic_queue.append(node_to_schedule.logic_queue[0])
        parent_node.weight = node_to_schedule.weight
        if parent_node.Busy:
            parent_node.s = parent_node.f
        else:
            parent_node.s = max(parent_node.f, parent_node.parent.Vt)
        parent_node.f = parent_node.s + (len(parent_node.logic_queue[0]) * 1.0) / parent_node.weight
        parent_node.Busy = True
        # update V(n)
        parent_node.Vt = node_to_schedule.f
    else:
        # ActivateChild <- 0
        parent_node.activeChild = None
        parent_node.Busy = False
    if parent_node != tree_root and len(parent_node.parent.logic_queue) == 0:
        restart_node(parent_node.parent)
    if parent_node == tree_root and len(tree_root.logic_queue) != 0:
        transmit_packet_to_link(parent_node)


def arrive(i, packet):
    global tree_root 
    leaf_node = leaf_list[i]
    parent_node = leaf_node.parent
    leaf_node.real_queue.append(packet)
    if len(leaf_node.logic_queue):
        return
    leaf_node.logic_queue.append(packet)
    leaf_node.s = max(leaf_node.f, parent_node.Vt)
    leaf_node.f = leaf_node.s + ((len(leaf_node.logic_queue[0]) * 1.0) / leaf_node.weight)
    if not parent_node.Busy:
        restart_node(parent_node)

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
t1.daemon = True

t3 = threading.Thread(target=getmetrics)
t3.daemon = True

t1.start()
# t2.start()
t3.start()

while threading.active_count() > 0:
    time.sleep(0.1)


