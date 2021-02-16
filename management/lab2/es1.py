
import random
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt


# ******************************************************************************
# Constants
# ******************************************************************************
Nbss = 5
chargerate = 20
# ARRIVAL = 100
SERVICE = 2*chargerate # av service time

ARRIVAL   = 600 # av inter-arrival time

waitingLine = []
batteryInCharge = []
inter_charge = 2*3600
SIM_TIME = 86400
w = 1800 # max waiting client mezz'ora = 1800?


class Measure:
    def __init__(self,Narr,Ndep,Loss,NAveraegUser,OldTimeEvent,AverageDelay,DelayDistr,WaitDel,NAveraegUserBuff,BusyTime):
        self.arr = Narr
        self.dep = Ndep
        self.loss=Loss
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
    def __init__(self,arrival_time):
        self.arrival_time = arrival_time

# ******************************************************************************
# station
# ******************************************************************************
class Station(object):

    # constructor
    def __init__(self,nReady=5,nCharge=0):
        self.nReady = nReady
        self.nCharge = nCharge
        # whether the station is idle or not
        # self.idle = True


# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue):
    
    # Cumulate statistic
    data.arr += 1
    
    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))
    
    # create a record for the client
    client = Client(time)

    # insert the record in the queue
    queue.append(client)    
    
    if station.nReady>0 :
        # print("Ready: ",station.nReady, " In charge", station.nCharge)
        station.nReady -= 1
        station.nCharge +=1
        chargeTime = inter_charge
        FES.put((time + chargeTime, "fullcharge"))
        print("Ready: ",station.nReady, " In charge", station.nCharge)
    else:
        if len(waitingLine) == Nbss:  # Se ho già un attesa per ogni batteria
            data.loss+=1
            return
        waitingLine.append([client,time+w]) #entra in coda e aspetta per w 
         

# ******************************************************************************

# fullcharges *******************************************************************
def fullcharge(time, FES, queue):

    # Cumulative statistic
    data.ut += len(waitingLine)*(time-data.oldT)
    data.oldT = time
    
    chargeTime = random.expovariate(1.0/SERVICE)
    # if no battery in charge return
    if station.nCharge == 0:
        return
    if len(queue) > 0 :
        client = queue.pop(0)
        chargeTime = inter_charge
        while len(waitingLine) > 0:
            Customer = waitingLine.pop(0)
            if Customer[1] > time:
                FES.put((time + chargeTime,
                         "fullcharge"))  # If not expired serve the customer (give the charged battery and retrieve the uncharged one, total doesn't change)
                return
            else:
                data.loss += 1
        # If no customer waiting
        station.nReady += 1
        station.nCharge -=1
        print("Ready: ",station.nReady, " In charge", station.nCharge)

        
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

random.seed(42)

data = Measure(0,0,0,0,0,0,[],0,0,0)

# the simulation time 
time = 0
# lost client
# loss = 0
# the list of events in the form: (time, type)
FES = PriorityQueue()

station = Station()
# schedule the first arrival at t=0
FES.put((0, "arrival"))

# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()
    if event_type == "arrival":
        arrival(time, FES, batteryInCharge)

    elif event_type == "fullcharge":
        fullcharge(time, FES, batteryInCharge)
    assert station.nReady+station.nCharge == Nbss

print("Missing service probability: ",data.loss/data.arr)

# print output data
# print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
      # data.arr,"- No. of fullcharges =",data.dep)

# print("Load: ",SERVICE/ARRIVAL)
# print("\nArrival rate: ",data.arr/time," - fullcharge rate: ",data.dep/time)

print("\nAverage number of users: ",data.ut/time)

# print("Average delay: ",data.delay/data.dep)
# print("Actual queue size: ",len(MM1))

# print("Average waiting in queue: ", data.waitDel/data.dep)
# print("Average waiting in queue of packets in queue: ",data.waitDel/countQ)
# print("Average number of user in queue: ", data.utBuffer/time)
# print("Busy time station: ", data.busyTime)
# PLot distribution
# x = data.delayDistr
# plt.hist(x,bins=100)    # It's an exponential
# plt.xlabel('Delay')
# plt.show()



# if len(MM1)>0:
    # print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
    
