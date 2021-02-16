#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue
import numpy as np
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD = 0.33
SERVICE = 10.0  # av service time
ARRIVAL = SERVICE / LOAD  # av inter-arrival time

TYPE1 = 1

SIM_TIME = 500000

arrivals = 0
users = 0
BusyServer = False

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

    def __init__(self):
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
        # service_time = random.expovariate(1.0 / SERVICE) #exponential distribution
        #service_time = random.uniform(SERVICE-5, SERVICE+5) #uniform distribution
        service_time = 10 #constant
        #v = np.random.binomial(size=1, n=1, p= 0.5) #bernoulli distribution
        #if(v[0] == 0):
        #    service_time = v0
        #else:
        #    service_time = v1

        #print('service_time', (service_time))

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
    global service_time
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
        #service_time = random.expovariate(1.0 / SERVICE) #exponential
        #service_time = random.uniform(SERVICE-5, SERVICE+5)  #uniform
        service_time = 10
        #v = np.random.binomial(size=1, n=1, p= 0.5) #bernoulli
        #if(v[0] == 0):
        #    service_time = v0
        #else:
        #    service_time = v1

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
    global BusyServer

    global MM1
    global waitBuffer
    global countQ
    global maxSize
    global nDropped
    global v0
    global v1

    random.seed(42)
    arrivals = 0
    users = 0
    BusyServer = False

    MM1 = []
    waitBuffer = []
    countQ = 0
    nDropped = 0
    data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)

    v0 = 5
    v1 = 15

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
    pi0 = (1-rho)/(1-pow(rho,maxSize+1))

    #E_s = (v0+v1)/2 #mean value
    E_s = 10
    #E_s2 = pow(v0,2)*0.5+pow(v1,2)*0.5 #bernoulli
    E2_s = pow((v0+v1)/2,2) #square mean value
    C2_s = (pow(10,2)/12)/100
    #C2_s = (E_s2 - E2_s)/E2_s #ratio
    rho = E_s*lam
    print('rho',rho)
    ss = (1+C2_s)/(2*(1-rho))
    E_T = E_s + (rho*E_s)*ss #average time
    E_N = rho + pow(rho,2)*((1+C2_s)/(2*(1-rho)))

    print('E[s]', E_s)
    print('E^2[s]', E2_s)
    print('C[s]', C2_s)
    print('E[T]', E_T)
    print('E[N]', E_N)
    print('rho', rho)

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

    print("Average delay, E[Tw+Ts]: ", data.delay/data.dep) #also the service time is included
    print("Actual queue size: ", len(MM1))
    if countQ > 0:
        print("Average waiting in queue of packets in queue E[Tw]: ", data.waitDel/countQ)
    print("Average waiting delay over all packets: ", data.waitDel/data.dep)
    print("Average number of user in queue E[Nw]: ", data.utBuffer/time)
    print("Average number of users in service E[Ns]: ", data.busyTime / time)

    print("Busy server probability: ", rho)

    print("Busy time server: ", data.busyTime)
    print("Dropped packets: ", nDropped)
    print("Loss probability: ", nDropped / data.arr)

    print("Loss probability (formula): ", ((1 - rho) / (1 - pow(rho, maxSize + 1))) * pow(rho, maxSize))

    if len(MM1) > 0:
        print("Arrival time of the last element in the queue:", MM1[len(MM1) - 1].arrival_time)

    return nDropped / data.arr


if __name__ == '__main__':
    global maxSize
    maxSize = 1000
    main()