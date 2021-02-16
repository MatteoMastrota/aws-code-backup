import random
from scipy import stats
import numpy as np
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt
import csv
# ******************************************************************************
# Constants
# ******************************************************************************
summerPrice=[]
winterPrice=[]
# Electricity price
with open("electricity_prices.csv") as csvFile:
    electricPrice = csv.reader(csvFile,delimiter=',')
    for row in electricPrice:
        summerPrice.append(float(row[5]))
        winterPrice.append(float(row[9]))
print("SUMMER ",summerPrice)
print("WINTER ",winterPrice)

Nbss = 5
CAPACITY = 40 #Kwh
chargerate = 10 #Kwh
# ARRIVAL = 100
SERVICE = 2 * chargerate  # av service time

ARRIVAL = 3600  # av inter-arrival time

f = 2
Tp = 7200
# Number of panelSizeW
S = 20
# Pick winter day
WMonth = "1"
WDay = "28"
winterEnergy = []
# Pick summer day
SMonth = "7"
SDay = "28"
summerEnergy = []
# Get Production Values
with open("PVproduction_PanelSize1kWp.csv") as csvFile:
    panelSizeW=csv.DictReader(csvFile,delimiter=',')
    for row in panelSizeW:
        if row["Month"]==WMonth and row["Day"]==WDay:
            winterEnergy.append(S* float(row["Output power (W)"]))
        elif row["Month"]==SMonth and row["Day"]==SDay:
            summerEnergy.append(S* float(row["Output power (W)"]))
print("Winter: ",sum(winterEnergy))
print("Summer: ",sum(summerEnergy))
totalEnergyUsed = {}
for i in range(25):
    totalEnergyUsed[i] = 1
TOTAL = 0    
waitingLine = []
batteryInCharge = []
inter_charge = 7200
SIM_TIME = 86400
w = 2000  # max waiting client

#modello l'arrival rate sulla base dell'orario: suddiviso in fasce
arrivalRate = {21600: ['t1',3600], 36000: ['t2',1800], 64800: ['t3',2500], 75600: ['t4',1800], 86400: ['t5',3600]}
Bth = 0.7*CAPACITY
timeSplit = {'t1': CAPACITY, 't2': Bth, 't3': CAPACITY, 't4': Bth, 't5': CAPACITY}

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
    def __init__(self, arrival_time,Charge):
        self.arrival_time = arrival_time
        self.charge = Charge


# ******************************************************************************
# station
# ******************************************************************************
class Station(object):

    # constructor
    def __init__(self, nReady=Nbss, nCharge=0,nPost=0):
        self.nReady = nReady
        self.nCharge = nCharge
        self.nPost = nPost
        # whether the station is idle or not
        # self.idle = True


# ******************************************************************************

def distrEnergyCharge(time,charge,chargeTime):
    chargePerSeconds = charge*1000/chargeTime
    # print(time)
    # print(chargeTime)
    startTime = time
    while startTime < time+chargeTime:
        # print(time+chargeTime)
        if int(startTime//3600)%24 <= 23:
            totalEnergyUsed[int(startTime//3600)%24] += chargePerSeconds
        # print(totalEnergyUsed[int(time//3600)])
        startTime +=1 

###################################################################################
def minPriceTime(time):
    index = int(time//3600)%24
    
    maxPostpone = time+Tp

    step = summerPrice[index:int(maxPostpone//3600)]
    # print(step)
    return np.argmin(step)+index

###################################################################################

def postponeCharge(time):
    proposedStart = minPriceTime(time)
    if int(time//3600) == proposedStart:
        return time
    else:
        return proposedStart*3600

# arrivals *********************************************************************
def arrival(time, FES, queue,status):
    global TOTAL
    global f
    # Cumulate statistic
    data.arr += 1

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    # create a record for the client
    batteryCharge = (random.randint(0,20)/100)*CAPACITY   #Battery remaining of arriving client kW
    # print(batteryCharge)
    client = Client(time,batteryCharge)

    # insert the record in the queue
    queue.append(client)

    if station.nReady > 0:
        # print("Ready: ", station.nReady, " In charge", station.nCharge)
        station.nReady -= 1
        # station.nCharge += 1
        capacity = timeSplit[status]
        chargeTime = (capacity-batteryCharge)/chargerate *3600
        distrEnergyCharge(time,capacity-batteryCharge,chargeTime)
        TOTAL += capacity-batteryCharge
        data.served += 1
        #data.waitDelDistr.append(0)
        data.waitDelDistr.append([time,data.waitDel/data.served])
        if station.nPost <= f:
            startCharge = postponeCharge(time)
            if startCharge != time: 
                station.nPost+=1
                FES.put((startCharge,"startCharge"))
            else:
                station.nCharge+=1
        else:
            station.nCharge+=1
        FES.put((startCharge + chargeTime, "charge"))
    else:
        # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaa")
        if len(waitingLine) == Nbss:  # Se ho già un attesa per ogni batteria
            data.loss += 1
            data.lossDistr.append([time,data.loss/data.arr])
            queue.pop()
            return
        waitingLine.append([client, time + w])  # entra in coda e aspetta al massimo w


# ******************************************************************************
def startCharge(time,FES,queue,status):
    station.nPost-=1
    station.nCharge+=1
    
# fullcharges *******************************************************************
def fullcharge(time, FES, queue,status):
    # Cumulative statistic
    global TOTAL
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
        if (time - client.arrival_time) <0:
            print(time)
            print(client.arrival_time)
            a =1/0
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
                capacity = timeSplit[status]
                chargeTime = (capacity-Customer[0].charge)/chargerate *3600
                TOTAL += capacity-Customer[0].charge
                distrEnergyCharge(time,capacity-Customer[0].charge,chargeTime)
                startCharge = postponeCharge(time)
                FES.put((startCharge + chargeTime,
                         "charge"))  # If not expired serve the customer (give the charged battery and retrieve the uncharged one, total doesn't change)
                return
            else:
                data.loss += 1
                data.lossDistr.append([time,data.loss/data.arr])

        # If no customer waiting
        station.nReady += 1
        station.nCharge -= 1
        # print("Ready: ", station.nReady, " In charge", station.nCharge)

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

HOUR = 0
# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()
    HOUR = int(time//3600)
    # print(time)
    for key in arrivalRate.keys():
        if time % 86400 <= key:
            ARRIVAL = arrivalRate[key][1]
            status = arrivalRate[key][0]
            break
        
    if event_type == "arrival":
        arrival(time, FES, batteryInCharge,status)

    elif event_type == "charge":
        fullcharge(time, FES, batteryInCharge,status)
        
    elif event_type == "startCharge":
        startCharge(time, FES, batteryInCharge,status)
    assert station.nReady + station.nCharge + station.nPost == Nbss
    # print("Batterie pronte: ",station.nReady)

print(TOTAL)
# a = 1/0
percentageClean = []
for element in totalEnergyUsed.keys():
    if element <= 23:
        percentageClean.append((summerEnergy[element]/totalEnergyUsed[element]*100))
print(percentageClean)
# a =1/0

noRenewable=0
for element in totalEnergyUsed.keys():
    # print(totalEnergyUsed[element]/1000000*summerPrice[element%24])
    noRenewable+=totalEnergyUsed[element]/1000000*summerPrice[element%24]
print("Spesa no rinnovabile ",noRenewable)

print(totalEnergyUsed)
withRenewable=0
for element in totalEnergyUsed.keys():
    if summerEnergy[element%24]:
        # print(element, " : ", (totalEnergyUsed[element]/1000000-summerEnergy[element%24]/1000000)*summerPrice[element%24])
        withRenewable+=(totalEnergyUsed[element]/1000000-summerEnergy[element%24]/1000000)*summerPrice[element%24]
    else:
        withRenewable+=totalEnergyUsed[element]/1000000*summerPrice[element%24]
        
print("Spesa con rinnovabile ",withRenewable)
print("Missing service probability, at the end: ", data.loss / data.arr)

# print output data
# print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
# data.arr,"- No. of fullcharges =",data.dep)

# print("Load: ",SERVICE/ARRIVAL)
# print("\nArrival rate: ",data.arr/time," - fullcharge rate: ",data.dep/time)

print("\nAverage number of users: ", data.ut / time)

print("Average delay: ",data.delay/data.served)
# print("Actual queue size: ",len(MM1))

print("Average waiting in queue: ", data.waitDel/data.served)
# print("Average waiting in queue of packets in queue: ",data.waitDel/countQ)
print("Average number of user in queue: ", data.utBuffer/time)
print("Busy time station: ", data.busyTime)
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


Rk = []
k_vect = []
for k in range(0, len(yy)):
    k_vect.append(k)
    yy_k = yy[k:]
    mean_k = np.mean(yy_k)
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

# test = data.waitDelDistr[100:]
x_hat = [x[1] for x in data.waitDelDistr]
m = np.mean(x_hat)
print("TOTAL mean: ",m)
s_2 = np.var(x_hat)
s = np.std(x_hat)
n = len(x_hat)
z = ([x-m for x in x_hat])/(s/ np.sqrt(n))
plt.hist(x_hat,bins=500)
plt.show()
print(stats.norm.interval(0.9,loc=m,scale=s/np.sqrt(len(x_hat))))