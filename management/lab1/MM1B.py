#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD = 0.5
SERVICE = 10.0  # av service time
ARRIVAL = SERVICE / LOAD  # av inter-arrival time
TYPE1 = 1

SIM_TIME = 500000

arrivals = 0
users = 0
BusyServer = False  # True: server is currently busy; False: server is currently idle

MM1 = []
waitBuffer = []
countQ = 0
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


# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue):
    global users
    global countQ
    global BusyServer
    global nDropped
    global maxSize
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
    if users == 1:
        BusyServer = True
        # sample the service time
        service_time = random.expovariate(1.0 / SERVICE)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
    else:
        #BusyServer = True
        if len(waitBuffer) < maxSize:
            countQ += 1
            waitBuffer.append(client)
            #data.utBuffer += len(waitBuffer) * (time - data.oldT)
        else:
            queue.pop(0)
            users -= 1
            nDropped += 1


# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue):
    global users
    global BusyServer
    # print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )

    # cumulate statistics
    data.dep += 1
    data.ut += users * (time - data.oldT)
    data.utBuffer += len(waitBuffer) * (time - data.oldT)
    data.oldT = time

    # get the first element from the queue
    client = queue.pop(0)

    # do whatever we need to do when clients go away

    data.delay += (time - client.arrival_time)
    data.delayDistr.append(time - client.arrival_time)  # record the queing delay
    users -= 1

    # see whether there are more clients to serve in the line
    if users > 0:
        # Liberate buffer
        BusyServer = True
        waitBuffer.pop(0)
        # Get waiting time in line
        data.waitDel += time - queue[0].arrival_time
        # sample the service time
        service_time = random.expovariate(1.0 / SERVICE)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
    else:
        BusyServer = False


# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************
def main():
    global data
    global arrivals
    global users
    global BusyServer  # True: server is currently busy; False: server is currently idle

    global MM1
    global waitBuffer
    global countQ
    global maxSize
    global nDropped

    random.seed(42)
    arrivals = 0
    users = 0
    BusyServer = False  # True: server is currently busy; False: server is currently idle

    MM1 = []
    waitBuffer = []
    countQ = 0
    nDropped = 0
    data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)

    # the simulation time
    time = 0

    # the list of events in the form: (time, type)
    FES = PriorityQueue()

    # schedule the first arrival at t=0
    FES.put((0, "arrival"))

    # simulate until the simulated time reaches a constant
    while time < SIM_TIME:
        (time, event_type) = FES.get()
        if BusyServer:
            data.busyTime += time - data.oldT
        if event_type == "arrival":
            arrival(time, FES, MM1)

        elif event_type == "departure":
            departure(time, FES, MM1)

    # print output data
    lam = 1/ARRIVAL
    mu = 1/SERVICE
    rho = SERVICE/ARRIVAL
    
    pi0 = (1-rho)/(1-pow(rho,(maxSize+1)+1))
    LossProb = ((1 - rho) / (1 - pow(rho, (maxSize +1)+ 1))) * pow(rho, maxSize+1)
    pi = 0
    
    if (maxSize > 0):
        for i in range(0, maxSize):
            pi += i * (pow(rho, i) * ((1 - rho) / (1 - pow(rho, maxSize + 1))))
        E_N = pi
        E_LAM = lam-lam*LossProb
        E_T = E_N/E_LAM
    else:
        #E_T = 1/(mu-lam)
        E_N = data.ut/time        
        E_LAM = lam-lam*(nDropped/data.arr) #arrival rate - LossProb*arrival rate
        E_T = E_N/E_LAM
        E_N = lam*E_T
        E_T_t = pi0/lam
        

    print("ARRIVAL: ", ARRIVAL)
    print("SERVICE: ", SERVICE)
    print("lamda: ", lam)
    print("mu:", mu)
    print("MEASUREMENTS \n\nNo. of users in the queue:", users, "\nNo. of arrivals =",
          data.arr, "- No. of departures =", data.dep, "Ergodicity condition: ", lam<mu)

    print("Load: ", SERVICE / ARRIVAL)
    print("\nArrival rate: ", data.arr / time, " - Departure rate: ", data.dep / time)

    print("\nAverage number of users E[N]: ", data.ut / time)
    #    print("Average number of users in the queue, formula E[N]: ", pow(LOAD,2)/(1-LOAD))

    print("Average delay, E[Tw+Ts]: ", data.delay/data.dep) #includo anche tempo di servizio
    print("Actual queue size: ", len(MM1))
    print("Average time spent waiting in queue E[Tw+Ts], formula: ", E_T)
    print("Average number of customer in the system E[N], Little's law formula: ", E_N)
    if countQ > 0:
        print("Average waiting in queue of packets in queue E[Tw]: ", data.waitDel/countQ)#something wrong
    print("Average waiting delay over all packets: ", data.waitDel/data.dep)
    # print("Average time spent in the waiting line E[Tw], formula: ", rho*(1/(mu - lam)))
    # print("\nAverage buffer occupancy: ", data.waitPackets / time)
    print("Average number of user in queue E[Nw]: ", data.utBuffer/time)
    # print("Average number of users in the waiting line E[Nw], formula: ", rho*(lam/(mu-lam)))
    print("Average number of users in service E[Ns]: ", data.busyTime / time)
    print("Average number of users in service E[Ns], formula: ", lam/mu)
    print("Average time in service E[Ts]: ", 1 / mu)

    print("Busy server probability: ", rho)

    print("Busy time server: ", data.busyTime)
    print("Dropped packets: ", nDropped)
    print("Loss probability: ", nDropped / data.arr)
    if maxSize == 0:
        print("Loss probability (formulaaa): ", pi0)
    else:
        print("Loss probability (formula): ", LossProb)

    if len(MM1) > 0:
        print("Arrival time of the last element in the queue:", MM1[len(MM1) - 1].arrival_time)

    return nDropped/data.arr

if __name__ == '__main__':
    global maxSize
    maxSize = -1
    main()