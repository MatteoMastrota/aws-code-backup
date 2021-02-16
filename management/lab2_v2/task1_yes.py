import random
from scipy import stats
import numpy as np
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt

# ******************************************************************************
# Constants
# ******************************************************************************
Nbss = 5
CAPACITY = 40 #Kwh
chargerate = 14 #Kwh
SERVICE = 2 * chargerate  # av service time
ARRIVAL = 2000  # av inter-arrival time

waitingLine = []
batteryInCharge = []
inter_charge = 7200
SIM_TIME = 86400*30
w = 3600  # max waiting client

class Measure:
    def __init__(self, Narr, Ndep, Loss, Served, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel,
                 NAveraegUserBuff, BusyTime, kWaitDel):
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
        self.KwaitDel = kWaitDel
        self.k = []


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, arrival_time,Charge):
        self.arrival_time = arrival_time
        self.charge = Charge


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
    batteryCharge = (random.randint(0,20)/100)*CAPACITY   #Battery remaining of arriving client
    print(batteryCharge)
    client = Client(time,batteryCharge)

    # insert the record in the queue
    queue.append(client)

    if station.nReady > 0:
        print("Ready: ", station.nReady, " In charge", station.nCharge)
        station.nReady -= 1
        station.nCharge += 1
        fullChargeTime = (CAPACITY-batteryCharge)/chargerate *3600
        data.served += 1
        data.waitDelDistr.append([time,data.waitDel/data.served])
        print(fullChargeTime)
        FES.put((time + fullChargeTime, "fullcharge"))
    else:
        if len(waitingLine) == Nbss:
            data.loss += 1
            data.lossDistr.append([time,data.loss/data.arr])
            queue.pop()
            return
        waitingLine.append([client, time + w])


# ******************************************************************************

# fullcharges *******************************************************************
def fullcharge(time, FES, queue):
    # Cumulative statistic
    data.ut += len(waitingLine) * (time - data.oldT)
    data.utBuffer += len(waitingLine) * (time - data.oldT)
    data.oldT = time

    chargeTime = 7200
    # if no battery in charge return
    if station.nCharge == 0:
        return
    if len(queue) > 0:
        client = queue.pop(0)
        data.delay += (time - client.arrival_time)
        while len(waitingLine) > 0:
            Customer = waitingLine.pop(0)
            if time < Customer[1]:
                data.served += 1
                data.waitDel += time - (Customer[1]-w)
                data.waitDelDistr.append([time,data.waitDel/data.served])
                if data.served > 74:
                    data.KwaitDel += time - (Customer[1] - w)
                    print(data.KwaitDel)
                    data.k.append([time,data.KwaitDel/(data.served-74)])
                fullChargeTime = (CAPACITY-Customer[0].charge)/chargerate *3600
                FES.put((time + fullChargeTime,
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

data = Measure(0, 0, 0, 0, 0, 0, 0, [], 0, 0, 0, 0)

# the simulation time
time = 0
# the list of events in the form: (time, type)
FES = PriorityQueue()
startFull = 0
station = Station(startFull,Nbss-startFull)
for i in range (Nbss-startFull):
    fullChargeTime = (CAPACITY-(random.randint(60,99)/100)*CAPACITY)/chargerate*3600
    print(fullChargeTime)
    FES.put((fullChargeTime, "fullcharge"))

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
    print("Batterie pronte: ",station.nReady)

print("Missing service probability, at the end: ", data.loss / data.arr)

print("\nAverage number of users: ", data.ut / time)

# Plot distribution
plt.xlabel("Time [seconds]")
plt.ylabel("Average waiting delay [seconds]")
plt.title("Average waiting delay")
plt.plot([x[0] for x in data.waitDelDistr],[x[1] for x in  data.waitDelDistr], label="Average waiting delay")
mean = np.mean([x[1] for x in  data.waitDelDistr])
my = np.transpose([[mean] * len([x[0] for x in data.waitDelDistr])])
plt.plot([x[0] for x in data.waitDelDistr], my, label="Mean")
plt.legend()
plt.savefig('avDelay_2batt.png')
plt.show()

xx = []
yy = []
dict = {}
for elem in data.lossDistr:
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
plt.xlabel('Time [second]')
plt.ylabel('Missed service probability')
plt.legend(loc=4)
#plt.savefig('miss_prob_deletek_.png')
plt.show()

#per eliminare warm-up transient period
yy = [x[1] for x in  data.waitDelDistr]
mean = np.mean(yy)

Rk = []
k_vect = []
mean_vect = []
for k in range(0, len(yy)):
    k_vect.append(k)
    yy_k = yy[k:]
    mean_k = np.mean(yy_k)
    mean_vect.append(mean_k)
    Rk.append((mean_k-mean)/mean)
plt.plot(k_vect,Rk)
plt.xlabel('k')
plt.ylabel('Rk')
plt.show()

x_hat = [x[1] for x in data.waitDelDistr]
m = np.mean(x_hat)
print("TOTAL mean: ",m)
s_2 = np.var(x_hat)
s = np.std(x_hat)
n = len(x_hat)
z = ([x-m for x in x_hat])/(s/ np.sqrt(n))
plt.hist(x_hat,bins=500)
plt.title("Delay distribution")
plt.xlabel("Delay [seconds]")
plt.ylabel("Probability")
plt.savefig("hist_delay.png")
plt.show()
print(stats.norm.interval(0.9,loc=m,scale=s/np.sqrt(len(x_hat))))

plt.xlabel("Time [seconds]")
plt.ylabel("Average waiting delay [seconds]")
plt.title("Average waiting delay (k)")
plt.plot([x[0] for x in data.k[1:]],[x[1] for x in  data.k[1:]], label="Average waiting delay from k")
mean = np.mean([x[1] for x in  data.k])
my = np.transpose([[mean] * len([x[0] for x in data.k])])
plt.plot([x[0] for x in data.k], my, label="Mean k")
plt.plot([x[0] for x in data.waitDelDistr],[x[1] for x in  data.waitDelDistr], label="Average waiting delay")
mean = np.mean([x[1] for x in  data.waitDelDistr])
my = np.transpose([[mean] * len([x[0] for x in data.waitDelDistr])])
plt.plot([x[0] for x in data.waitDelDistr], my, label="Mean")
plt.legend()
#plt.savefig("av_cut.png")
plt.show()

x_hat = [x[1] for x in data.k]
m = np.mean(x_hat)
print("TOTAL mean: ",m)
s_2 = np.var(x_hat)
s = np.std(x_hat)
n = len(x_hat)
z = ([x-m for x in x_hat])/(s/ np.sqrt(n))
plt.hist(x_hat,bins=500)
plt.title("Delay distribution")
plt.xlabel("Delay [seconds]")
plt.ylabel("Probability")
plt.savefig("hist_delay_k.png")
plt.show()
print(stats.norm.interval(0.9,loc=m,scale=s/np.sqrt(len(x_hat))))