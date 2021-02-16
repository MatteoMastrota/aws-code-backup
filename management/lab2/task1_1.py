import random
import numpy as np
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
Nbss = 5
chargerate = 20
# ARRIVAL = 100
SERVICE = 2 * chargerate  # av service time

ARRIVAL = 600  # av inter-arrival time

waitingLine = []
batteryInCharge = []
inter_charge = 7200
SIM_TIME = 864000
w = 2500  # max waiting client


class Measure:
    def __init__(self, Narr, Ndep, Loss, Served, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel,
                 NAveraegUserBuff, BusyTime):
        self.arr = Narr
        self.dep = Ndep
        self.loss = Loss
        self.served = Served
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.waitDelDistr = []
        self.lossDistr = []
        self.waitDel = WaitDel
        self.utBuffer = NAveraegUserBuff
        self.busyTime = BusyTime


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time


# ******************************************************************************
# station
# ******************************************************************************
class Station(object):

    # constructor
    def __init__(self, nReady=Nbss, nCharge=0):
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
    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    # create a record for the client
    client = Client(time)

    # insert the record in the queue
    queue.append(client)

    if station.nReady > 0:
        print("Ready: ", station.nReady, " In charge", station.nCharge)
        station.nReady -= 1
        station.nCharge += 1
        chargeTime = inter_charge
        data.served += 1
        #data.waitDelDistr.append(0)
        data.waitDelDistr.append([time,data.waitDel/data.served])
        FES.put((time + chargeTime, "fullcharge"))
    else:
        if len(waitingLine) == Nbss:  # Se ho già un attesa per ogni batteria
            data.loss += 1
            data.lossDistr.append([time,data.loss/data.arr])
            queue.pop()
            return
        waitingLine.append([client, time + w])  # entra in coda e aspetta al massimo w


# ******************************************************************************

# fullcharges *******************************************************************
def fullcharge(time, FES, queue):
    # Cumulative statistic
    data.ut += len(waitingLine) * (time - data.oldT)
    data.utBuffer += len(waitingLine) * (time - data.oldT)
    data.oldT = time

    #chargeTime = random.expovariate(1.0 / SERVICE)
    chargeTime = 7200
    # if no battery in charge return
    if station.nCharge == 0:
        return
    if len(queue) > 0:
        client = queue.pop(0)
        data.delay += (time - client.arrival_time) # BATTERIE
        # chargeTime = inter_charge
        while len(waitingLine) > 0:
            Customer = waitingLine.pop(0)
            #print(time - Customer[1])
            #data.waitDelDistr.append(time - (Customer[1]-w))
            if time < Customer[1]: #se il cliente in attesa non ha ancora raggiunto il suo massimo
                #time (=arrivo+carica) < Customer[1] (=arrivo+maxWait) -> carica<maxWait
                data.served += 1
                data.waitDel += time - (Customer[1]-w)
                data.waitDelDistr.append([time,data.waitDel/data.served])
                # data.waitDelDistr.append([time - (Customer[1]-w), len(waitingLine)])
                FES.put((time + chargeTime,
                         "fullcharge"))  # If not expired serve the customer (give the charged battery and retrieve the uncharged one, total doesn't change)
                return
            else:
                data.loss += 1
                data.lossDistr.append([time,data.loss/data.arr])

        # If no customer waiting
        station.nReady += 1
        station.nCharge -= 1
        print("Ready: ", station.nReady, " In charge", station.nCharge)

# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

random.seed(42)

data = Measure(0, 0, 0, 0, 0, 0, 0, [], 0, 0, 0)

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
    assert station.nReady + station.nCharge == Nbss

print("Missing service probability, at the end: ", data.loss / data.arr)

# print output data
# print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
# data.arr,"- No. of fullcharges =",data.dep)

# print("Load: ",SERVICE/ARRIVAL)
# print("\nArrival rate: ",data.arr/time," - fullcharge rate: ",data.dep/time)

print("\nAverage number of users: ", data.ut / time)

# print("Average delay: ",data.delay/data.dep)
# print("Actual queue size: ",len(MM1))

# print("Average waiting in queue: ", data.waitDel/data.dep)
# print("Average waiting in queue of packets in queue: ",data.waitDel/countQ)
# print("Average number of user in queue: ", data.utBuffer/time)
# print("Busy time station: ", data.busyTime)
# Plot distribution

plt.plot([x[0] for x in data.waitDelDistr],[x[1] for x in  data.waitDelDistr])
plt.show()


xx = []
yy = []
dict = {}
for elem in data.lossDistr:
    #xx.append(elem[0])
    #yy.append(elem[1])
    dict[elem[0]] = elem[1]
keys = dict.keys()
keys = sorted(keys)
for elem in keys:
    xx.append(elem)
    yy.append(dict[elem])
mean = np.mean(yy)

print('Missed service probability, mean: ',np.mean(yy))
my = np.transpose([[mean] * len(xx)])
plt.plot(xx,yy, label='Missed service probability')
plt.plot(xx,my, label='Mean value')
# plt.hist(x,bins=100)    # It's an exponential
plt.xlabel('Time [second]')
plt.ylabel('Missed service probability')
plt.legend(loc=4)
plt.savefig('miss_prob_deletek_.png')
plt.show()

# print('len di yy', len(yy))
#per eliminare warm-up transient period
yy = [x[1] for x in  data.waitDelDistr]
mean = np.mean(yy)

print("TOTAL mean: ",mean)

Rk = []
k_vect = []
for k in range(0, len(yy)):
    k_vect.append(k)
    yy_k = yy[k:]
    mean_k = np.mean(yy_k)
    # print(mean_k)
    Rk.append((mean_k-mean)/mean)
plt.plot(k_vect,Rk)
plt.xlabel('k')
plt.ylabel('Rk')
plt.show()

#stable = 0
#i = 0
#j = i
#while i < len(yy) and stable < 5:
#for i in range (0,len(yy)):
    #print(yy[i])
#    if yy[i]>(mean-0.01) and yy[i]<(mean+0.01):
#        stable +=1
#        print('arrivo ad un valore vicino alla media dopo elemento: ', i)
#    i += 1

#run con Nbss = 2
#Missed service probability, mean:  0.7969604212721231
#run con Nbss = 5
#Missed service probability, mean:  0.5373317032887762
##run con Nbss = 10
#Missed service probability, mean:  0.19448167396906266

x_hat = [x[1] for x in  data.waitDelDistr]
m = np.mean(x_hat)
s_2 = np.var(x_hat)
n = len(x_hat)
z = ([x-m for x in x_hat])/(np.sqrt(s_2/n))

z = (x_hat-m)/(np.sqrt(s_2/n))
print('z',z)










