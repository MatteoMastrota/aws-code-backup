import random
from math import factorial
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
transmNumber = 1
serverNumber = 5
LOAD = 0.85
SERVICE = 10.0  # av service time
mu = 1/SERVICE
lam = (LOAD*mu*serverNumber)/transmNumber

print('LOAD_def', LOAD)
ARRIVAL = 1/lam
TYPE1 = 1

SIM_TIME = 500000

arrivals = 0
users = 0
BusyServer = False  # True: server is currently busy; False: server is currently idle

MM1 = []
waitBuffer = []
countQ = 0
maxSize = 500
nDropped = 0

# print(ARRIVAL)
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


# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):

    # constructor
    def __init__(self):
        # whether the server is idle or not
        self.idle = True
        self.time = 0
        self.id = -1
        self.busyTime = 0
        self.cost = 0


# ******************************************************************************

def freeServer():
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

def serverChoice(free):
    min = 1000
    for i in range(0, len(free)):
        if free[i].cost < min:
            min = free[i].cost
            index = i
    return index

# arrivals *********************************************************************
def arrival(time, FES, queue,ix):
    global users
    global countQ
    global BusyServer
    global nDropped
    global servers
    global index
    global free

    print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )

    # cumulate statistics
    data.arr += 1
    data.ut += users * (time - data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)

    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival",-1))

    users += 1

    # create a record for the client
    client = Client(TYPE1, time)

    # insert the record in the queue
    queue.append(client)

    # if the number of users is lower or equal to the number of servers -> vuol dire che ne ho uno per ciascuno
    if users <= serverNumber:
        #BusyServer = True
        # sample the service time
        service_time = random.expovariate(1.0 / SERVICE)
        # service_time = 1 + random.uniform(0, SEVICE_TIME)

        #quali sono i servers liberi
        free = freeServer()
        #ix = random.choice(free)
        #index = random.randrange(len(free))  # select random server
        #scelgo il server a minor costo computazionale
        index = serverChoice(free)
        #assegno al cliente che inizierà il servizio l'indice del server
        client.index = free[index].id

        #occupo il server con tale indice e setto il time di inizio "occupazione"
        servers[free[index].id].idle = False
        servers[free[index].id].time = time

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure", client.index))
    else:
        #se il numero di utenti supera il numero di servers, vuol dire che devo mettere in coda
        #BusyServer = True
        #se la coda non è ancora piena
        if len(waitBuffer) <= maxSize:
            countQ += 1
            waitBuffer.append(client)
        else:
        #se la coda è piena, devo rinunciare al cliente
            queue.pop(0)
            users -= 1
            nDropped += 1


# ******************************************************************************
def enterFromQueue():
    if len(waitBuffer) != 0:
        waitClient = waitBuffer.pop(0)
        servers[index].idle = False
        servers[free[index]].time = time


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

    if len(queue) > 0:
        print("Index leaving ", ix)
        print("Coda ", len(queue))
        for c in queue:
            print(c.index)
            if c.index == ix:
                client = c
                queue.remove(c)
                break
    else:
        return

    data.delay += (time - client.arrival_time)
    data.delayDistr.append(time - client.arrival_time)  # record the queing delay
    # users -= 1
    # see whether there are more clients to in the line
    #se ci sono ancora utenti nella coda
    if users >= serverNumber:
        users -= 1
        # Liberate buffer
        #BusyServer = True

        # Get waiting time in line
        try:
            data.waitDel += time - queue[0].arrival_time
        except IndexError as index:
            pass
        # sample the service time
        service_time = random.expovariate(1.0 / SERVICE)

        #busy = busyServer()
        #index = random.choice(busy)
        # index = random.randrange(len(busy)) # select random server
        #devo liberare quello che era stato selezionato ed occupato dal cliente
        #debug
        #print('voglio liberare il server di ',client, client.index)
        #index = dict[client]
        index = client.index
        #libero il server che era stato occupato dal cliente che ho estratto dalla coda
        servers[index].idle = True
        print(index)
        servers[index].busyTime += time - servers[index].time
        #debug
        #for i in range (0,len(servers)):
        #    print('server appena liberato', index, servers[i].idle, i)
        #se ci sono clienti in coda
        if len(waitBuffer) != 0:
            #estraggo un cliente dalla coda
            waitClient = waitBuffer.pop(0)
            free = freeServer()

            print([i.id for i in free])
            #cerco un server libero da assegnare al nuovo cliente
            index = serverChoice(free)
            #waitClient.index = index
            waitClient.index = free[index].id
            #occupo il server con il nuovo cliente estratto dalla waiting line
            #servers[index].idle = False
            servers[waitClient.index].idle = False
            servers[waitClient.index].time = time
            free = freeServer()

            print([i.id for i in free])
            # schedule when the client will finish the server
            FES.put((time + service_time, "departure", waitClient.index))
            #debug
            #print('ero in coda ed ho subito occupato il server', index)
            #servers[index].time = time
    else:
        users -= 1
        index = client.index
        free = freeServer()

        print([i.id for i in free])
        # libero il server che era stato occupato dal cliente che ho estratto dalla coda
        servers[index].idle = True
        print(index)
        servers[index].busyTime += time - servers[index].time
        free = freeServer()

        print([i.id for i in free])
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
FES.put((0, "arrival",-1))

# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type, ix) = FES.get()
    if BusyServer:
        data.busyTime += time - data.oldT
    if event_type == "arrival":
        arrival(time, FES, MM1,ix)

    elif event_type == "departure":
        departure(time, FES, MM1, ix)

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

print("Load: ", SERVICE / ARRIVAL)
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
    print("ID: ",server.id," Cost: ",server.cost," Busy time server: ", server.busyTime)
if len(MM1) > 0:
    print("Arrival time of the last element in the queue:", MM1[len(MM1) - 1].arrival_time)
