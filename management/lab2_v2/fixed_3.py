import random
from scipy import stats
import numpy as np
from queue import Queue, PriorityQueue
import matplotlib.pyplot as plt
import csv

# ******************************************************************************
# Constants
# ******************************************************************************
summerPrice = []
winterPrice = []
# Electricity price
with open("electricity_prices.csv") as csvFile:
    electricPrice = csv.reader(csvFile, delimiter=',')
    for row in electricPrice:
        summerPrice.append(float(row[5]))
        winterPrice.append(float(row[9]))
#print("SUMMER ", sum(summerPrice)) #vettori contenenti il costo per ora in un giorno d'estate (o inverno)
#print("WINTER ", winterPrice)

#Nbss = 5
CAPACITY = 40  # Kwh
#chargerate = 10  # Kwh
  # av service time
#ARRIVAL = 3600  # av inter-arrival time

f = -1 #number of station that can be postponed
Tp = 4000 #max amount of time for which the battery can be postponed

#case a
S = 20
Nbss = 10
chargerate = 5
# SERVICE = 2 * chargerate
#miss del 0.5
#wait circa 200
################################################
#case b
# S = 20
# Nbss = 10
# chargerate = 5
# SERVICE = 2 * chargerate
#miss 0.35
#wait circa 200
##################################################
#case c
# S = 20
# Nbss = 10
# chargerate = 10
# SERVICE = 2 * chargerate
#raddoppiando f ottengo un gain invernale maggiore
#miss 0.13
#wait circa 100
################################################
#case d
# S = 10
# Nbss = 5
# chargerate = 5
# SERVICE = 2 * chargerate
#miss 0.5
#wait circa 200
################################################
#case e
# S = 10
# Nbss = 10
# chargerate = 5
# SERVICE = 2 * chargerate
#miss 0.35
#wait circa 200
################################################
#case ff
# S = 10
# Nbss = 5
# chargerate = 10
# SERVICE = 2 * chargerate
#miss 0.13
#wait circa 120
#################################

arrivalRate = {21600: ['t1', 3600], 36000: ['t2', 720], 64800: ['t3', 1800], 75600: ['t4', 800], 86400: ['t5', 3600]}
Bth = 0.7 * CAPACITY
timeSplit = {'t1': 0.8*CAPACITY, 't2': Bth, 't3': 0.7*CAPACITY, 't4': Bth, 't5': 0.8*CAPACITY}

#winter day
WMonth = "1"
WDay = "28"
winterEnergy = []
#summer day
SMonth = "7"
SDay = "28"
summerEnergy = []

# Get Production Values
with open("PVproduction_PanelSize1kWp.csv") as csvFile:
    panelSizeW = csv.DictReader(csvFile, delimiter=',')
    for row in panelSizeW:
        if row["Month"] == WMonth and row["Day"] == WDay:
            winterEnergy.append(S * float(row["Output power (W)"]))
        elif row["Month"] == SMonth and row["Day"] == SDay:
            summerEnergy.append(S * float(row["Output power (W)"]))
print("Winter day production of green energy [W]: ", sum(winterEnergy))
print("Summer day production of green energy [W]: ", sum(summerEnergy))

totalEnergyUsed = {}
#each element represent the amount of energy needed at that hour
for i in range(24):
    totalEnergyUsed[i] = 1

TOTAL_CAPACITY = 0
waitingLine = []
batteryInCharge = []
inter_charge = 7200
SIM_TIME = 86400
w = 2000  #max waiting client

#modello l'arrival rate sulla base dell'orario: suddiviso in fasce
# arrivalRate = {21600: ['t1', 3600], 36000: ['t2', 1800], 64800: ['t3', 2500], 75600: ['t4', 1800], 86400: ['t5', 3600]}
# Bth = 0.7 * CAPACITY
# timeSplit = {'t1': CAPACITY, 't2': Bth, 't3': CAPACITY, 't4': Bth, 't5': CAPACITY}


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
    def __init__(self, arrival_time, Charge):
        self.arrival_time = arrival_time
        self.charge = Charge

# ******************************************************************************
# station
# ******************************************************************************
class Station(object):
    # constructor
    def __init__(self, nReady=Nbss, nCharge=0, nPost=0):
        self.nReady = nReady
        self.nCharge = nCharge
        self.nPost = nPost
        # self.idle = True

# ******************************************************************************

def distrEnergyCharge(time, charge, chargeTime):
    '''
    :param time: actual time
    :param charge: total capacity - battery charge at the arrival
    :param chargeTime: time needed to be recharged
    to evaluate the total energy used in seconds
    '''
    chargePerSeconds = charge * 1000 / chargeTime
    # print(time)
    # print(chargeTime)
    startTime = time
    while startTime < time + chargeTime:
        # print(time+chargeTime)
        if int(startTime // 3600) % 24 <= 23:
            totalEnergyUsed[int(startTime // 3600) % 24] += chargePerSeconds
        # print(totalEnergyUsed[int(time//3600)])
        startTime += 1

    ###################################################################################


def minPriceTime(time):
    '''
    :return: time in which the price reaches the minimum value,
            considering the time window [actual time, actual time+max amount of postponed time]
    '''
    index = int(time // 3600) % 24

    maxPostpone = time + Tp
    # step = summerPrice[index:int(maxPostpone // 3600)+1]
    step = winterPrice[index:int(maxPostpone // 3600)+1]
    return np.argmin(step) + index

###################################################################################

def postponeCharge(time):
    '''
    :return: proposed time to start the recharging process in order to save money
    '''
    proposedStart = minPriceTime(time)
    if int(time // 3600) == proposedStart:
        return time
    else:
        print("POSTPONE")
        return proposedStart * 3600


# arrivals *********************************************************************
def arrival(time, FES, queue, status):
    global TOTAL_CAPACITY
    global f

    data.arr += 1

    #sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)
    #schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    #create a record for the client
    batteryCharge = (random.randint(0, 20) / 100) * CAPACITY  #battery remaining of arriving client

    client = Client(time, batteryCharge)

    queue.append(client)

    if station.nReady > 0:
        #print("Ready: ", station.nReady, " In charge", station.nCharge)
        station.nReady -= 1
        #station.nCharge += 1
        capacity = timeSplit[status]
        chargeTime = (capacity - batteryCharge) / chargerate * 3600
        distrEnergyCharge(time, capacity - batteryCharge, chargeTime)
        TOTAL_CAPACITY += capacity - batteryCharge #amount of energy needed to recharge the batteries
        data.served += 1
        # data.waitDelDistr.append(0)
        data.waitDelDistr.append([time, data.waitDel / data.served])
        if station.nPost <= f:
            startCharge = postponeCharge(time)
            if startCharge != time:
                #if the proposedTime is different from the actual one, the recharge is postponed
                station.nPost += 1
                FES.put((startCharge, "startCharge"))
            else:
                #otherwiser the recharging process starts
                station.nCharge += 1
        else:
            #if the max number of postponed batteries is already reached
            startCharge=time
            station.nCharge += 1
        FES.put((startCharge + chargeTime, "charge"))
    else:
        if len(waitingLine) == Nbss:
            #if there is already a vehicle waiting for each battery, a missed seervice occurs
            data.loss += 1
            data.lossDistr.append([time, data.loss / data.arr])
            queue.pop()
            return
        waitingLine.append([client, time + w])
        #client inserted in the waiting line, it waits for a time lower or equal to w


# ******************************************************************************
def startCharge(time, FES, queue, status):
    station.nPost -= 1
    station.nCharge += 1


# fullcharges *******************************************************************
def fullcharge(time, FES, queue, status):
    global TOTAL_CAPACITY

    data.ut += len(waitingLine) * (time - data.oldT)
    data.utBuffer += len(waitingLine) * (time - data.oldT)
    data.oldT = time

    # chargeTime = random.expovariate(1.0 / SERVICE)
    #chargeTime = 7200

    # if no battery in charge return
    if station.nCharge == 0:
        return
    if len(queue) > 0:
        client = queue.pop(0)
        data.delay += (time - client.arrival_time)  #batteries delay
        if (time - client.arrival_time) < 0:
            print(time)
            #print(client.arrival_time)
        # chargeTime = inter_charge
        while len(waitingLine) > 0:
            Customer = waitingLine.pop(0)
            # print(time - Customer[1])
            # data.waitDelDistr.append(time - (Customer[1]-w))
            if time < Customer[1]:
                #if the client's maximum time has not expired yet
                # time (=arrivo+carica) < Customer[1] (=arrivo+maxWait) -> carica<maxWait
                data.served += 1
                data.waitDel += time - (Customer[1] - w) #vehicle's delay
                data.waitDelDistr.append([time, data.waitDel / data.served])
                # data.waitDelDistr.append([time - (Customer[1]-w), len(waitingLine)])
                capacity = timeSplit[status]
                chargeTime = (capacity - Customer[0].charge) / chargerate * 3600
                TOTAL_CAPACITY += capacity - Customer[0].charge
                distrEnergyCharge(time, capacity - Customer[0].charge, chargeTime)
                if station.nPost <= f:
                    startCharge = postponeCharge(time)
                    if startCharge != time:
                        #if the proposedTime is different from the actual one, the recharge is postponed
                        station.nPost += 1
                        station.nCharge-=1
                        FES.put((startCharge, "startCharge"))
                else:
                    startCharge = time
                FES.put((startCharge + chargeTime,
                         "charge"))  # If not expired serve the customer (give the charged battery and retrieve the uncharged one, total doesn't change)
                return
            else:
                #if the maximum time has already expired, the customer is lost
                data.loss += 1
                data.lossDistr.append([time, data.loss / data.arr])

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
    HOUR = int(time // 3600)
    # print(time)
    for key in arrivalRate.keys():
        if time % 86400 <= key:
            ARRIVAL = arrivalRate[key][1]
            status = arrivalRate[key][0]
            break

    if event_type == "arrival":
        arrival(time, FES, batteryInCharge, status)

    elif event_type == "charge":
        fullcharge(time, FES, batteryInCharge, status)

    elif event_type == "startCharge":
        startCharge(time, FES, batteryInCharge, status)
    print(event_type)
    print("Ready: ",station.nReady,"CHARGE ",station.nCharge, "POST ",station.nPost)
    assert station.nReady + station.nCharge + station.nPost == Nbss
    # print("Batterie pronte: ",station.nReady)

print("Total energy needed [kW]", TOTAL_CAPACITY)
# a = 1/0
percentageClean = []
for element in totalEnergyUsed.keys():
    if element <= 23:
        percentageClean.append((summerEnergy[element] / totalEnergyUsed[element] * 100))
        # percentageClean.append((winterEnergy[element] / totalEnergyUsed[element] * 100))
print("Percentage Clean: ", percentageClean)
# a =1/0

#noRenewable=0
#withRenewable=0

noRenewable=[]
for element in totalEnergyUsed.keys():
    #noRenewable+=totalEnergyUsed[element]/1000000*summerPrice[element % 24]
    # noRenewable.append(totalEnergyUsed[element] / 1000000 * summerPrice[element % 24])
    noRenewable.append(totalEnergyUsed[element] / 1000000 * winterPrice[element % 24])
print("Spesa noRenewable € = ", sum(noRenewable))

withRenewable=[]
for element in totalEnergyUsed.keys():
    # withRenewable.append((totalEnergyUsed[element] / 1000000 - summerEnergy[element % 24] / 1000000) * summerPrice[element % 24])
    withRenewable.append((totalEnergyUsed[element] / 1000000 - winterEnergy[element % 24] / 1000000) * winterPrice[element % 24])
    # withRenewable += (totalEnergyUsed[element]/1000000 - summerEnergy[element % 24]/1000000) * summerPrice[element % 24]
print("Spesa withRenewable € = ", sum(withRenewable))
print(withRenewable)

gain = []
for i in range (len(noRenewable)):
    gain.append(noRenewable[i]-withRenewable[i])

print("Missing service probability, at the end: ", data.loss / data.arr)

xx = []
yy = []
dict = {}
for elem in data.lossDistr:
    # xx.append(elem[0])
    # yy.append(elem[1])
    dict[elem[0]] = elem[1]
keys = dict.keys()
keys = sorted(keys)
for elem in keys:
    xx.append(elem)
    yy.append(dict[elem])
mean = np.mean(yy)

print('Missed service probability, mean: ', np.mean(yy))
my = np.transpose([[mean] * len(xx)])
plt.plot(xx, yy, label='Missed service probability')
plt.plot(xx, my, label='Mean value')
# plt.hist(x,bins=100)    # It's an exponential
plt.xlabel('Time [hour]')
plt.ylabel('Missed service probability')
plt.savefig('SummvsWint_miss.png')
plt.show()

yy = []
xx = []
plt.title('Waiting delay distribution')
plt.plot([x[0] for x in data.waitDelDistr], [x[1] for x in data.waitDelDistr], label = 'Waiting delay distribution')
for x in data.waitDelDistr:
    xx.append(x[0])
    yy.append(x[1])
mean = np.mean(yy)
my = np.transpose([[mean] * len(yy)])
plt.plot(xx, my, label='Mean value')
#plt.hist(x,bins=100)    # It's an exponential
plt.xlabel('Time [hour]')
plt.ylabel('Waiting delay')
plt.legend(loc=4)
plt.savefig('SummvsWint_wait.png')
plt.show()

print(gain)

#sumgain = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.31253983766956583, 0.4807168546499998, 0.6200159759478261, 0.6896030609782606, 0.714824479065217, 0.7024522363304349, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565168, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
#summerGain_c = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.31253983766956583, 0.4807168546499998, 0.6200159759478261, 0.6896030609782606, 0.714824479065217, 0.7024522363304346, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565168, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
#summerGain_b = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.3125398376695654, 0.4807168546499998, 0.6200159759478265, 0.6896030609782615, 0.7148244790652174, 0.7024522363304349, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565212, 0.015560286808695256, 0.0, 0.0, 0.0, 0.0]
summerGain_a = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442950000134, 0.059396967904347786, 0.1642114670086956, 0.3125398376695654, 0.48071685465, 0.6200159759478264, 0.6896030609782611, 0.7148244790652174, 0.7024522363304347, 0.6216893878847833, 0.5020476122065219, 0.33638984311739106, 0.1909318770891304, 0.08105290799565212, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
#summerGain_f =[0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.31253983766956583, 0.4807168546499998, 0.6200159759478261, 0.6896030609782606, 0.714824479065217, 0.7024522363304346, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565168, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
#summerGain_e = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.3125398376695654, 0.4807168546499998, 0.6200159759478265, 0.6896030609782615, 0.7148244790652174, 0.7024522363304349, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565212, 0.015560286808695256, 0.0, 0.0, 0.0, 0.0]
#summerGain_d = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442950000134, 0.059396967904347786, 0.1642114670086956, 0.3125398376695654, 0.48071685465, 0.6200159759478264, 0.6896030609782611, 0.7148244790652174, 0.7024522363304347, 0.6216893878847833, 0.5020476122065219, 0.33638984311739106, 0.1909318770891304, 0.08105290799565212, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
#summerGain_c = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.31253983766956583, 0.4807168546499998, 0.6200159759478261, 0.6896030609782606, 0.714824479065217, 0.7024522363304346, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565168, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
#summerGain_b = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.3125398376695654, 0.4807168546499998, 0.6200159759478265, 0.6896030609782615, 0.7148244790652174, 0.7024522363304349, 0.6216893878847833, 0.5020476122065216, 0.3363898431173913, 0.19093187708913018, 0.08105290799565212, 0.015560286808695256, 0.0, 0.0, 0.0, 0.0]
#summerGain = [0.0, 0.0, 0.0, 0.0, 0.0, 0.007143442949999912, 0.059396967904347786, 0.1642114670086956, 0.3125398376695654, 0.4807168546499998, 0.6200159759478261, 0.6896030609782613, 0.7148244790652174, 0.7024522363304349, 0.6216893878847831, 0.5020476122065218, 0.3363898431173915, 0.19093187708913062, 0.08105290799565257, 0.0155602868086957, 0.0, 0.0, 0.0, 0.0]
hours = np.linspace(0,24,24)
plt.plot(hours, summerGain_a, label='Summer day')
plt.xlabel('Time [hour]')
plt.ylabel('Gain [Euro]')
plt.plot(hours, gain, label='Winter day')
plt.legend(loc=2)
plt.savefig('SummvsWint.png')
plt.show()

print(percentageClean)
#sumperc = [0.0, 0.0, 0.0, 0.0, 0.0, 0.19688703295761079, 1.6371647247682763, 3.4215332547117976, 4.947885090233827, 7.687903120963088, 10.607727692601502, 11.818161818373051, 14.16366434508703, 17.607534412286284, 15.891651562322462, 20.097632936572918, 16.705980967409996, 4.540368621032654, 1.7198792723703629, 0.7717067892887074, 0.0, 0.0, 0.0, 0.0]
#.0, 0.0, 0.09907052375878482, 0.5334746652529518, 1.062730463915898, 1.3910595804561114, 2.581022355818245, 3.2816023188793424, 2.157574207787866, 1.7604781333241737, 0.8063845823326143, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
summerPerc_a = [0.0, 0.0, 0.0, 0.0, 0.0, 0.43452017487540007, 4.622693770244732, 17.256168745027338, 21.94124032809177, 31.76719970248238, 40.42014319425933, 47.271229150818876, 61.037932984234054, 55.008656795458485, 66.60749301994203, 42.59069634499132, 22.4902493492395, 11.6674533018642, 5.105593778042339, 1.1411429428527342, 0.0, 0.0, 0.0, 0.0]
#summerPerc_b = [0.0, 0.0, 0.0, 0.0, 0.0, 0.23838354865379352, 2.126692728017328, 6.175208817404964, 10.385014858494419, 16.121714695783183, 20.210475790469204, 23.636087278236907, 25.438413147252977, 26.930262767015584, 25.07720305627194, 30.070024678475026, 16.02585274878887, 6.002579116922448, 2.389472210554017, 0.5065789717047058, 0.0, 0.0, 0.0, 0.0]
#summerPerc_c = [0.0, 0.0, 0.0, 0.0, 0.0, 0.19688703295761079, 1.6371647247682763, 3.4215332547117976, 4.947885090233827, 7.687903120963088, 11.186366129821959, 13.200947210856977, 23.684491683864213, 30.046613525671628, 20.709312732576343, 20.097632936572918, 16.705980967409996, 4.540368621032654, 1.7198792723703629, 0.7717067892887074, 0.0, 0.0, 0.0, 0.0]
#summerPerc_d = [0.0, 0.0, 0.0, 0.0, 0.0, 0.43452017487540007, 4.622693770244732, 17.256168745027338, 21.94124032809177, 31.76719970248238, 40.42014319425933, 47.271229150818876, 61.037932984234054, 55.008656795458485, 66.60749301994203, 42.59069634499132, 22.4902493492395, 11.6674533018642, 5.105593778042339, 1.1411429428527342, 0.0, 0.0, 0.0, 0.0]
#summerPerc_e = [0.0, 0.0, 0.0, 0.0, 0.0, 0.23838354865379352, 2.126692728017328, 6.175208817404964, 10.385014858494419, 16.121714695783183, 20.210475790469204, 23.636087278236907, 25.438413147252977, 26.930262767015584, 25.07720305627194, 30.070024678475026, 16.02585274878887, 6.002579116922448, 2.389472210554017, 0.5065789717047058, 0.0, 0.0, 0.0, 0.0]
#summerPerc_f = [0.0, 0.0, 0.0, 0.0, 0.0, 0.19688703295761079, 1.6371647247682763, 3.4215332547117976, 4.947885090233827, 7.687903120963088, 11.186366129821959, 13.200947210856977, 23.684491683864213, 30.046613525671628, 20.709312732576343, 20.097632936572918, 16.705980967409996, 4.540368621032654, 1.7198792723703629, 0.7717067892887074, 0.0, 0.0, 0.0, 0.0]
#summerPerc = [0.0, 0.0, 0.0, 0.0, 0.0, 0.29604129893877185, 2.5267353607005, 5.202975940479529, 9.85856282874028, 18.662209143942672, 21.219563751571904, 29.25244424642608, 36.84540651774209, 39.6194793506932, 25.771975859351855, 23.591040424298924, 16.33631470008022, 6.75167809399258, 2.44641825205713, 0.45647087058244273, 0.0, 0.0, 0.0, 0.0]
hours = np.linspace(0,24,24)
plt.plot(hours, summerPerc_a, label='Summer day')
plt.xlabel('Time [hour]')
plt.ylabel('Percentage of green energy used')
plt.plot(hours, percentageClean, label='Winter day')
plt.legend(loc=2)
plt.savefig('SummvsWintPerc_C_t.png')
plt.show()