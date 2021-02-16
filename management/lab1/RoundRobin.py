import random
from math import factorial
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
LOAD = (transmNumber*lam)/(mu*serverNumber)
print('LOAD_def', LOAD)
ARRIVAL = 1/lam
TYPE1 = 1
print(ARRIVAL)

SIM_TIME = 500000

arrivals = 0
users = 0
BusyServer = False  # True: server is currently busy; False: server is currently idle

MM1 = []
waitBuffer = []
countQ = 0
maxSize = 50
nDropped = 0

turnAround = 2

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
        self.index = -1
        self.service_time = 0
        self.residual_time = 0

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
        self.cost = 0
        self.id = -1


# ******************************************************************************

def freeServer():
    '''
        return a Server vector composed by the idle servers
    '''
    global servers
    free = []
    for i in range(0,serverNumber):
        if servers[i].idle == True:
            free.append(servers[i])
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
    global servers
    global index
    global free
    global turnAround

    # print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )

    # cumulate statistics
    data.arr += 1
    data.ut += users * (time - data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)

    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival", -1))

    users += 1

    # create a record for the client
    client = Client(TYPE1, time)

    # insert the record in the queue
    client.service_time = random.expovariate(1.0 / SERVICE)
    #at the arrival, the residual time is equal to the service time
    client.residual_time = client.service_time
    queue.append(client)

    #idle servers
    free = freeServer()
    if len(free) > 0:
        index = random.randint(0,len(free)-1)  # select random server
        #the client is assigned to the selected server
        client.index = free[index].id
        servers[client.index].idle = False
        servers[client.index].time = time

        #if the service time is lower than a turnAround, the client will leave after its service time so a departure event is schedule
        if client.service_time <= turnAround:
            #print("Immediate departure at ", client.index)
            FES.put((time + client.service_time, "departure", client.index))
        
        #otherwise, a rotation event is scheduled since at least one turnAround is needed
        else:
            #print(client.index, "index event rotation in arrival")
            FES.put((time + turnAround, "event_rotation", client.index))

    else:
        if len(waitBuffer) <= maxSize:
            countQ += 1
            waitBuffer.append(client)
        else:
            queue.pop(0)
            users -= 1
            nDropped += 1

    
# rotation *******************************************************************
def rotation(time, FES, queue, ix):
    count=0
    global users
    
    #search for the actual client
    if len(queue) > 0:
        print("Lunghezza queue: ",len(queue))
        print(queue)
        for c in queue:
            #ix is the server that has to be liberate since it has already served a client for a turnAround
            #print("CODA", len(queue), "BUF", len(waitBuffer))
            if c.index == ix:
                count+=1
                client = c
                # queue.remove(c) #
                # break

    queue.remove(client)
    client.residual_time = client.residual_time - turnAround
    servers[ix].idle = True
    servers[ix].busyTime += turnAround

    data.delay += turnAround
    data.delayDistr.append(turnAround)

    client.index = -1
    queue.append(client)
    
    if len(waitBuffer) > 0:
        next_client = waitBuffer.pop(0)
        waitBuffer.append(client)
    else:
        waitBuffer.append(client)
        next_client = waitBuffer.pop(0)

    #search for an idle server
    free = freeServer()
    index = random.randint(0,len(free)-1) #select random server
    
    #assign to the client the selected server
    next_client.index = free[index].id
    servers[next_client.index].idle = False
    servers[next_client.index].time = time
    
    if next_client.residual_time <= turnAround:
        #print("Next CLient departure ", next_client.index)
        FES.put((time + next_client.residual_time, "departure", next_client.index))
    else:
        #print("NEXT CLIENT ROTATION ", next_client.index)
        FES.put((time + turnAround, "event_rotation", next_client.index))
    
    
# departures *******************************************************************
def departure(time, FES, queue, ix):
    global users
    global BusyServer
    global servers
    # print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )

    # cumulate statistics
    data.dep += 1
    data.ut += users * (time - data.oldT)
    data.utBuffer += len(waitBuffer) * (time - data.oldT)
    data.oldT = time

    #search for the actual client
    if len(queue) > 0:
        for c in queue:
            if c.index==ix:
                client = c
                queue.remove(c)
                break

    else:
        return

    servers[ix].idle = True
    servers[ix].busyTime += turnAround
    data.delay += turnAround
    data.delayDistr.append(turnAround)  # record the queing delay

    # see whether there are more clients to in the line
    if users > 0:
        users -= 1
        # Liberate buffer
        #BusyServer = True

        # Get waiting time in line
        try:
            data.waitDel += time - queue[0].arrival_time
        except IndexError as ix:
            pass

        if len(waitBuffer) != 0:
            waitClient = waitBuffer.pop(0)
            for q in queue:
                if q == waitClient:
                    client = q
                    
            free = freeServer()
            index = random.randint(0,len(free)-1)
            client.index = free[index].id
            servers[client.index].idle = False
            servers[client.index].time = time
            #occupo il server con il nuovo cliente estratto dalla waiting line

            #if waitClient.service_time <= turnAround:
            if client.service_time <= turnAround:
                FES.put((time + client.service_time, "departure", client.index))
            else:
                FES.put((time + turnAround, "event_rotation", client.index))



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
c = 20
for i in range(serverNumber):
    servers.append(Server())
    servers[i].cost = c
    servers[i].id = i
    c = c-3

# schedule the first arrival at t=0
FES.put((0, "arrival", -1))

# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type, index) = FES.get()
    print(event_type,index)
    if BusyServer:
        data.busyTime += time - data.oldT

    if event_type == "arrival":
        arrival(time, FES, MM1)

    elif event_type == "event_rotation":
        rotation(time, FES, MM1, index)

    elif event_type == "departure":
        departure(time, FES, MM1, index)

lam = 1/ARRIVAL
mu = 1/(SERVICE)#*serverNumber)
first = 0
for i in range (0,serverNumber):
    first += pow(lam/mu,i)/factorial(i)
#second = (pow(lam/mu,serverNumber)/factorial(serverNumber))*(1/(1-(SERVICE/ARRIVAL)))
second = (((pow(lam/(serverNumber*mu),serverNumber))/(1- (lam/(serverNumber*mu))))*(pow(serverNumber, serverNumber)/factorial(serverNumber)))
pi0 = 1/(first+second)

print("SERVICE",SERVICE)
print("ARRIVAL",ARRIVAL)
print("lam", lam)
print("mu", mu)
print("first", first)
print("second", second)
print("pi0", pi0)

#Nw = (pi0*pow(lam/mu,serverNumber)*(SERVICE/ARRIVAL))/(factorial(serverNumber)*pow(1-(SERVICE/ARRIVAL),2))
pim = pi0*1/factorial(serverNumber)*pow(lam/mu,serverNumber)
Nw = (serverNumber*lam*mu*pim)/pow(serverNumber*mu-lam,2)
Tw = (serverNumber*mu*pim)/pow(serverNumber*mu-lam,2)

# print output data
print("MEASUREMENTS \n\nNo. of users in the queue:", users, "\nNo. of arrivals =",
      data.arr, "- No. of departures =", data.dep, "Ergodicity condition: ", lam<(serverNumber*mu))

print("Load: ", lam / (serverNumber*mu))
print("\nArrival rate: ", data.arr / time, " - Departure rate: ", data.dep / time)
print("Actual queue size: ", len(MM1))

#print("Average queuing delay (all the system): ", data.delay / data.dep)
#print("Average time spent in the queue E[T]: ", 1 /(serverNumber*mu - lam)) no
print("\nAverage number of users, E[N]: ", data.ut / time)
#print("Average number of users, E[N] formula: ", lam*((Nw/lam)+1/mu))
print("Average number of users, E[N] formula: ", Nw+lam/mu)

print("Average delay E[Tw+Ts]: ", data.delay / data.dep)
print("Average time in the system, E[T] formula: ", Tw+1/(serverNumber*mu))

print("Average waiting in queue E[Tw] over all packets: ", data.waitDel / data.dep)
#print("Average waiting in queue E[Tw], formula: ", Nw/lam)
print("Average waiting in queue E[Tw], formula: ", Tw)#coincidono
if countQ != 0:
    print("Average waiting of packets in queue, E[Tw]: ", data.waitDel / countQ)
print("Average number of customers waiting in line, E[Nw] formula: ", Nw)
print("Average number of user in queue, E[Nw]: ", data.utBuffer / time)
#print("Average number of user in queue, E[Nw]: ", countQ / time)

print("E[Ts], formula: ", 1/(serverNumber*mu))
print("E[Ts]: ", data.delay / data.dep - data.waitDel / data.dep)
print("Dropped packets: ", nDropped)
print("Loss probability: ", nDropped / data.arr)

print("Probability that no customers are in the system: ", pi0)

for server in servers:
    print("Busy time server: ", server.busyTime)
if len(MM1) > 0:
    print("Arrival time of the last element in the queue:", MM1[len(MM1) - 1].arrival_time)
