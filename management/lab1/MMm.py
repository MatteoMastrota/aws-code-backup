#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
transmNumber = 1
serverNumber = 5
LOAD = 0.33
SERVICE = 10.0  # av service time
mu = 1/SERVICE
lam = (LOAD*mu*serverNumber)/transmNumber
ARRIVAL = 1/lam
LOAD = (transmNumber*lam)/(mu*serverNumber)
print('LOAD_def', LOAD)
TYPE1 = 1
c = 0
SIM_TIME = 500000

arrivals = 0
users = 0
BusyServer = False  # True: server is currently busy; False: server is currently idle

MMm = []
waitBuffer = []
countQ = 0
maxSize = 50
nDropped = 0

# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel, NAveraegUserBuff,
                 BusyTime):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.delayDistr = DelayDistr
        self.waitDel = WaitDel
        self.utBuffer = NAveraegUserBuff
        self.busyTime = BusyTime


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, type, arrival_time):
        self.type = type
        self.arrival_time = arrival_time

# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):
    # constructor
    def __init__(self):
        # whether the server is idle or not
        self.idle = True
        self.time = 0
        self.busyTime = 0

# ******************************************************************************

def freeServer():
    global servers
    free = []
    for i in range(serverNumber):
        if servers[i].idle == True:
            free.append(i)
    return free

def busyServer():
    global servers
    busy = []
    for i in range(serverNumber):
        if servers[i].idle == False:
            busy.append(i)
    return busy

# arrivals *********************************************************************
def arrival(time, FES, queue):
    global users
    global countQ
    global BusyServer
    global nDropped
    global c
    global servers
    # print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )

    # cumulate statistics
    data.arr += 1
    data.ut += users * (time - data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)

    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    users += 1

    # create a record for the client
    client = Client(TYPE1, time)

    # insert the record in the queue
    queue.append(client)

    # if the server is idle start the service
    if users <= serverNumber:
        BusyServer = True
        # sample the service time
        service_time = random.expovariate(1 / SERVICE)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        free = freeServer()
        ix = random.choice(free)
        index = random.randrange(len(free))  # select random server

        servers[free[index]].idle = False
        servers[free[index]].time = time
    else:
        BusyServer = True
        if len(waitBuffer) <= maxSize:
            waitBuffer.append(client)
        else:
            queue.pop(0)
            users -= 1
            nDropped += 1


# departures *******************************************************************
def departure(time, FES, queue):
    global users
    global BusyServer
    global countQ
    global servers
    global c
    # print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )

    # get the first element from the queue
    if len(queue) > 0:
        client = queue.pop(0)
    else:
        return
        # cumulate statistics
    data.dep += 1
    data.ut += users * (time - data.oldT)
    data.utBuffer += len(waitBuffer) * (time - data.oldT)
    data.oldT = time

    data.delay += (time - client.arrival_time)
    data.delayDistr.append(time - client.arrival_time)  # record the queing delay
    users -= 1

    busy = busyServer()
    index = random.choice(busy) # select random server
    servers[index].idle = True
    servers[index].busyTime += time - servers[index].time

    # see whether there are more clients to in the line
    if users >= serverNumber:
        # Liberate buffer
        BusyServer = True

        # sample the service time
        service_time = random.expovariate(1 / SERVICE)
        c += 1
        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))

        data.waitDel += time - waitBuffer[0].arrival_time

        countQ += 1
        waitClient = waitBuffer.pop(0)
        servers[index].idle = False
        servers[index].time = time


# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

random.seed(42)

data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)

# the simulation time
time = 0

# the list of events in the form: (time, type)
FES = PriorityQueue()
# Initialize servers
servers = []
for i in range(serverNumber):
    servers.append(Server())

# schedule the first arrival at t=0
FES.put((0, "arrival"))

# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()
    if BusyServer:
        data.busyTime += time - data.oldT
    if event_type == "arrival":
        arrival(time, FES, MMm)

    elif event_type == "departure":
        departure(time, FES, MMm)

# print output data
print("MEASUREMENTS \n\nNo. of users in the queue:", users, "\nNo. of arrivals =",
      data.arr, "- No. of departures =", data.dep)

print("Load: ", transmNumber*lam/(serverNumber*mu))
print("\nArrival rate: ", data.arr / time, " - Departure rate: ", data.dep / time)

print("\nAverage number of users: ", data.ut / time)

print("Average delay: ", data.delay / data.dep)
print("Actual queue size: ", len(MMm))

print("Average waiting time in queue: ", data.waitDel / data.dep)

if countQ != 0:
    print("Average waiting time in queue of packets in queue: ", data.waitDel / countQ)
print("Average number of user in waiting line: ", data.utBuffer / time)
print("Busy time server: ", data.busyTime)
print("Dropped packets: ", nDropped)
print("Loss probability: ", nDropped / data.arr)


for server in servers:
    print("server busy time: ", server.busyTime)
if len(MMm) > 0:
    print("Arrival time of the last element in the queue:", MMm[len(MMm) - 1].arrival_time)
