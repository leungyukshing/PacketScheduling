import socket
import sys
import time
import threading
from collections import deque
from collections import defaultdict

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

# metrics variable
packet_received = 0
packet_sent = 0


# activeConn = 0 # UNUSED
# iters = {0:0, 1:0, 2:0} # UNUSED
# count = 0 # UNUSED

ER = 0
EB = 1
IR = 2
IB = 3
IDLE = 4


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
            # print('length:', len(leaf_list[int(sourcey)].real_queue), 'source:', sourcey)
            packet = Packet(sourcey, data, packet_size[sourcey])
            enque(packet, flows_qfq[sourcey])
    # s.close()


def sendpacket():
    global realT
    while True:
        if destination_address:
            packet = packet_deque()
            s.sendto(str.encode(packet.data), destination_address)
            time.sleep(sleeptime[packet.source])


class Flow:
    def __init__(self, s: 0, f: 0, queue, group_id: 0, weight: 0) -> None:
        self.s = s
        self.f = f
        self.queue = queue
        self.group_id = group_id
        self.weight = weight

class Group:
    def __init__(self,s: 0, f: 0, id, buckets) -> None:
        self.s = s
        self.f = f
        self.id = id
        self.buckets = buckets

class Packet:
    def __init__(self, source, data, length) -> None:
        self.source = source
        self.data = data
        self.length = length


# initialize 32 groups
groups = []
for i in range(32):
    buckets = defaultdict(deque)
    groups.append(Group(0, 0, i, buckets))
set = {ER: 0, EB: 0, IR: 0, IB: 0}
V = 0



flows_qfq = [Flow(weight=2),  Flow(weight=4), Flow(weight=1)]


def bucket_insert(flow, g):
    return


def ffs(x):
    if x == 0:
        return None
    return (x & ~x).bit_length()() - 1

def ffs_from(x, index):
    x >> index
    return ffs(x) + index

def fls(x):
    n = 32

    if x == 0:
        return -1
    if x & 0xFFFF0000 == 0:
        x <<= 16
        n -= 16
    if x & 0xF0000000 == 0:
        x <<= 8
        n -= 8
    if x & 0xC0000000 == 0:
        x <<= 2
        n -= 2
    if x & 0x80000000 == 0:
        x <<= 1
        n -= 1
    return n - 1


def bucket_head_remove(buckets):
    buckets[min(buckets.keys())].queue.popleft()

def enque(packet: Packet, flow: Flow):
    global V
    flow.queue.append(packet)
    if len(flow.queue) != 1:
        return
    flow.s = max(flow.f, V)
    flow.f = flow.s + packet.length * 1.0 / flow.weight
    g = groups[flow.group_id]
    if (len(g.buckets[min(g.buckets.keys())].queue) == 0 or flow.s < g.s): # to be inplemented !!!!!!!!!!
        set[IR] &= ~(1 << g.id)
        set[IB] &= ~(1 << g.id)
        g.s = flow.s & ~(2 ** g.id - 1)
        g.f = g.s + 2 * (2 ** g.id)
    bucket_insert(flow, g)

    if set[ER] == 0 and V < g.s:
        V = g.s
    state = compute_group_state(g)
    set[state] |= 1 << g.id


def compute_group_state(g):
    s = ER if g.s <= V else EB
    x = ffs_from(set[ER], g.id)
    s = s + IB if x != None and groups[x].F < g.F else s + IR
    return s

def packet_deque():
    global V
    if set[ER] == 0:
        return
    g = groups[ffs(set[ER])]
    flow = bucket_head_remove(g.buckets)
    packet = flow.queue.popleft()

    flow.s = flow.f
    if len(flow.queue) != 0:
        p = flow.queue[0]
        flow.f = flow.s + p.length / flow.weight
        bucket_insert(flow. g)

    old_V = V
    V += packet.length
    old_F = g.F
    if len(g.buckets[min(g.buckets.keys())].queue) == 0:
        state = IDLE
    else:
        g.s = g.buckets[min(g.buckets.keys())].s
        g.f = g.buckets[min(g.buckets.keys())].f
        state = compute_group_state(g)

    if state == IDLE or g.f > old_F:
        set[ER] &= ~(1 << g.id)
        set[state] |= 1 << g.id
        unblock_groups(g.id, old_F)

    x = set[ER] | set[IB]
    if x != 0:
        if set[ER] == 0:
            V = max(V, groups[ffs(x)].s)
        make_eligible(old_V, V)
    return packet

def move_groups(mask, src, dest):
    set[dest] |= set[src] & mask
    set[src] &= ~(set[src] & mask)

def make_eligible(V1, V2):
    i = fls(V1 ^ V2)
    mask = (1 << (i + 1)) - 1
    move_groups(mask, IR, ER)
    move_groups(mask, IB, EB)


def unblock_groups(i, old_F):
    x = ffs(set[ER])
    if x == None or groups[x].F > old_F:
        mask = (1 << i) - 1
        move_groups(mask, EB, ER)
        move_groups(mask, IB, IR)


 
t1 = threading.Thread(target=recvpacket)
t1.daemon = True
# t2 = threading.Thread(target=sendpacket)
# t2.daemon = True

t1.start()
# t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)


