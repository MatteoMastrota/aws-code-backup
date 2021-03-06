#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.5
SERVICE = 10.0 # av service time
ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1 

SIM_TIME = 500000

arrivals=0
users=0
BusyServer=False # True: server is currently busy; False: server is currently idle

MM1=[]
waitBuffer = []
countQ = 0
nDropped = 0
# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay,DelayDistr,WaitDel,NAveraegUserBuff,BusyTime):
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
    def __init__(self,type,arrival_time):
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
    #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
    data.arr += 1
    data.ut += users*(time-data.oldT)
    data.oldT = time
    
    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    users += 1
    
    # create a record for the client
    client = Client(TYPE1,time)

    # insert the record in the queue
    queue.append(client)

    # if the server is idle start the service
    if users==1:
        BusyServer = True
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)
        #service_time = 1 + random.uniform(0, SEVICE_TIME)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
    else:
        BusyServer = True
        if len(waitBuffer)<= maxSize:
            countQ += 1
            waitBuffer.append(client)
        else :
            queue.pop(0)
            users -= 1
            nDropped += 1
# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue):
    global users
    global BusyServer
    #print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )
        
    # cumulate statistics
    data.dep += 1
    data.ut += users*(time-data.oldT)
    data.utBuffer += len(waitBuffer)*(time-data.oldT)
    data.oldT = time
    
    # get the first element from the queue
    client = queue.pop(0)
    
    # do whatever we need to do when clients go away
    
    data.delay += (time-client.arrival_time)
    data.delayDistr.append(time-client.arrival_time)    # record the queing delay
    users -= 1
    
    # see whether there are more clients to in the line
    if users >0:
        # Liberate buffer
        BusyServer = True
        waitBuffer.pop(0)
        # Get waiting time in line
        data.waitDel += time-queue[0].arrival_time
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)

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
    global BusyServer # True: server is currently busy; False: server is currently idle

    global MM1
    global waitBuffer
    global countQ 
    global maxSize
    global nDropped 


    random.seed(42)
    arrivals=0
    users=0
    BusyServer=False # True: server is currently busy; False: server is currently idle

    MM1=[]
    waitBuffer = []
    countQ = 0
    nDropped = 0
    data = Measure(0,0,0,0,0,[],0,0,0)

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
            data.busyTime += time-data.oldT
        if event_type == "arrival":
            arrival(time, FES, MM1)

        elif event_type == "departure":
            departure(time, FES, MM1)
            
    # print output data
    print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
          data.arr,"- No. of departures =",data.dep)

    print("Load: ",SERVICE/ARRIVAL)
    print("\nArrival rate: ",data.arr/time," - Departure rate: ",data.dep/time)

    print("\nAverage number of users: ",data.ut/time)

    print("Average delay: ",data.delay/data.dep)
    print("Actual queue size: ",len(MM1))

    print("Average waiting in queue: ", data.waitDel/data.dep)
    if countQ==0:
        realWait=0
    else:
        realWait=data.waitDel/countQ
        print("Average waiting in queue of packets in queue: ",data.waitDel/countQ)
    print("Average number of user in queue: ", data.utBuffer/time)
    print("Busy time server: ", data.busyTime)
    print("Dropped packets: ", nDropped)
    print("Loss probability: ", nDropped/data.arr)


    if len(MM1)>0:
        print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
    # PLot distribution
    # x = data.delayDistr
    # plt.hist(x,bins=100)    # It's an exponential
    # plt.xlabel('Delay')                  
    # plt.show()
    return nDropped/data.arr, data.waitDel/data.dep, realWait , data.ut/time  , data.busyTime,data.arr,data.utBuffer/time

    
if __name__ == '__main__':
    global maxSize
    i0 = LOAD
    rho = []
    eN = []
    maxSize = -1 
    colors = {0 : 'green', 5: 'red', 10 : 'blue' , 15 : 'yellow' ,20: 'orange' }
    lossProbabilities = {}
    wait= {}
    realWaitDict= {}
    cust= {}
    serverBusy= {}
    arrivi= {}
    custQueue = {}
    
    while maxSize <=20:
        i = i0 
        while i < 10:
            LOAD = i 
            rho.append(LOAD)
            lossProbabilities[LOAD]=[]
            wait[LOAD]=[]
            realWaitDict[LOAD]=[]
            cust[LOAD]=[]
            serverBusy[LOAD]=[]
            arrivi[LOAD]=[]
            custQueue[LOAD]=[]
            
            ARRIVAL   = SERVICE/LOAD # av inter-arrival time
            loss,waiting,realWait,avgCust,serverB,arr,avgCustQueue = main()
            lossProbabilities[LOAD].append(loss)
            wait[LOAD].append(waiting)
            realWaitDict[LOAD].append(realWait)
            cust[LOAD].append(avgCust)
            serverBusy[LOAD].append(serverB)
            arrivi[LOAD].append(arr)
            custQueue[LOAD].append(avgCustQueue)
            
            eN.append(loss)
            i += 0.5
        # PLot distribution

        # plt.plot(rho,eN,label='B='+str(maxSize),color = colors[maxSize])    # It's an exponential
        # plt.ylabel('Loss probability')
        # plt.xlabel('Load')
        # # plt.show()
        maxSize+=10
    # plt.ylabel('Loss probability')
    # plt.xlabel('Load')
    # plt.title('M/M/1')
    # plt.legend(loc='lower right')
    # plt.show()
        
    