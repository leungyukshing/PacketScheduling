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
packet_size = [100, 50, 100]  # maybe we should read from the input?
numpackets = [2, 4, 1]  # weights
sleeptime = [0.1, 0.05, 0.1]
global_start_time = None  # record the first packet arrival time
flag = 0  # used to initialize states
rDash = 0  # rate for
realT = 0 #current real time

# metrics variable
packet_received = 0
packet_sent = 0


# activeConn = 0 # UNUSED
# iters = {0:0, 1:0, 2:0} # UNUSED
# count = 0 # UNUSED

def recvpacket():
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
            print('length:', len(leaf_list[int(sourcey)].real_queue), 'source:', sourcey)
            arrive(int(sourcey), data)
    # s.close()


def sendpacket():
    global realT
    while True:
        if destination_address:
            mini = INT_MAX
            index = 0
            so = 0
            for i in range(3):
                for j in range(len(source[i]['fno'])):
                    if source[i]['sent'][j] == 0 and source[i]['eligibility'][j] == 1:
                        if source[i]['fno'][j] < mini:
                            mini = min(source[i]['fno'])
                            index = j
                            so = i
            if mini != INT_MAX:
                s.sendto(str.encode(source[so]['data'][index]), destination_address)
                realT += packet_size[so]
                source[so]['sent'][index] = 1
            time.sleep(sleeptime[so])


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
    # set Vt of dummy root
    node.parent.Vt = node.f
    s.sendto(str.encode(node.logic_queue[0]), destination_address)
    reset_path(node)
    

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



class Flow:
    def __init__(self, weight) -> None:
        self.s = 0
        self.f = 0
        self.V = 0
        self.queue = deque()
        self.group = None
        self.weight = weight



flows_qfq = [Flow(weight=2),  Flow(weight=4), Flow(weight=1)]

#i : flow index
def enque(i, package):
    flow = flows_qfq[i]
    flow.queue.append(package)
    if (flow.queue[0]!=package):
        return
    flow.s = max(flow.f, flow.V)
    flow.f = flow.s + len(package) * 1.0 /     







 
t1 = threading.Thread(target=recvpacket)
t1.daemon = True
# t2 = threading.Thread(target=sendpacket)
# t2.daemon = True

t1.start()
# t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)


