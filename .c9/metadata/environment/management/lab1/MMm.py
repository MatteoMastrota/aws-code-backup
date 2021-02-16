{"filter":false,"title":"MMm.py","tooltip":"/management/lab1/MMm.py","undoManager":{"mark":12,"position":12,"stack":[[{"start":{"row":0,"column":0},"end":{"row":308,"column":0},"action":"remove","lines":["","import random","from math import factorial","from queue import Queue, PriorityQueue","import matplotlib.pyplot as plt","","# ******************************************************************************","# Constants","# ******************************************************************************","serverNumber = 5","transNumber = 2","#ARRIVAL = 30","#ARRIVAL = ARRIVAL / transNumber","SERVICE = 10.0 * serverNumber  # av service time","#LOAD = SERVICE/ARRIVAL","LOAD = 0.33","ARRIVAL = SERVICE / LOAD  # av inter-arrival time","print(\"ARRIVAL def:\", ARRIVAL)","TYPE1 = 1","","SIM_TIME = 500000","","arrivals = 0","users = 0","BusyServer = False  # True: server is currently busy; False: server is currently idle","","MMm = []","waitBuffer = []","countQ = 0","maxSize = 0","nDropped = 0","#transNumber = 2","#ARRIVAL = ARRIVAL / transNumber","","","# print(ARRIVAL)","# ******************************************************************************","# To take the measurements","# ******************************************************************************","class Measure:","    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel, NAveraegUserBuff,","                 BusyTime):","        self.arr = Narr","        self.dep = Ndep","        self.ut = NAveraegUser","        self.oldT = OldTimeEvent","        self.delay = AverageDelay","        self.delayDistr = DelayDistr","        self.waitDel = WaitDel","        self.utBuffer = NAveraegUserBuff","        self.busyTime = BusyTime","","","# ******************************************************************************","# Client","# ******************************************************************************","class Client:","    def __init__(self, type, arrival_time):","        self.type = type","        self.arrival_time = arrival_time","","","# ******************************************************************************","# Server","# ******************************************************************************","class Server(object):","","    # constructor","    def __init__(self):","        # whether the server is idle or not","        self.idle = True","        self.time = 0","        self.busyTime = 0","","","# ******************************************************************************","","def freeServer():","    global servers","    free = []","    for i in range(serverNumber):","        if servers[i].idle == True:","            free.append(i)","    return free","","","def busyServer():","    global servers","    busy = []","    for i in range(serverNumber):","        if servers[i].idle == False:","            busy.append(i)","    return busy","","","# arrivals *********************************************************************","def arrival(time, FES, queue):","    global users","    global countQ","    global BusyServer","    global nDropped","    global servers","    global index","    global free","    # print(\"Arrival no. \",data.arr+1,\" at time \",time,\" with \",users,\" users\" )","","    # cumulate statistics","    data.arr += 1","    data.ut += users * (time - data.oldT)","    data.oldT = time","","    # sample the time until the next event","    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)","","    # schedule the next arrival","    FES.put((time + inter_arrival, \"arrival\"))","","    users += 1","","    # create a record for the client","    client = Client(TYPE1, time)","","    # insert the record in the queue","    queue.append(client)","","    # if the server is idle start the service","    if users <= serverNumber:","        BusyServer = True","        # sample the service time","        service_time = random.expovariate(1.0/SERVICE)","        # service_time = 1 + random.uniform(0, SEVICE_TIME)","","        # schedule when the client will finish the server","        FES.put((time + service_time, \"departure\"))","        free = freeServer()","        ix = random.choice(free)","        index = random.randrange(len(free))  # select random server","        # print(ix)","        # print(free)","        servers[free[index]].idle = False","        servers[free[index]].time = time","    else:","        BusyServer = True","        if len(waitBuffer) <= maxSize:","            countQ += 1","            waitBuffer.append(client)","        else:","            queue.pop(0)","            users -= 1","            nDropped += 1","","","# ******************************************************************************","def enterFromQueue():","    if len(waitBuffer) != 0:","        waitClient = waitBuffer.pop(0)","        servers[index].idle = False","        servers[free[index]].time = time","","","# departures *******************************************************************","def departure(time, FES, queue):","    global users","    global BusyServer","    global servers","    # print(\"Departure no. \",data.dep+1,\" at time \",time,\" with \",users,\" users\" )","","    # cumulate statistics","    data.dep += 1","    data.ut += users * (time - data.oldT)","    data.utBuffer += len(waitBuffer) * (time - data.oldT)","    data.oldT = time","    # get the first element from the queue","    if len(queue) > 0:","        client = queue.pop(0)","    else:","        return","        # do whatever we need to do when clients go away","","    data.delay += (time - client.arrival_time)","    data.delayDistr.append(time - client.arrival_time)  # record the queing delay","    # users -= 1","","    # see whether there are more clients to in the line","    if users >= serverNumber:","        users -= 1","        # Liberate buffer","        BusyServer = True","","        # Get waiting time in line","        try:","            data.waitDel += time - queue[0].arrival_time","        except IndexError as index:","            pass","        # sample the service time","        service_time = random.expovariate(1.0/SERVICE)","","        # schedule when the client will finish the server","        FES.put((time + service_time, \"departure\"))","","        busy = busyServer()","        index = random.choice(busy)","        # index = random.randrange(len(busy)) # select random server","        servers[index].idle = True","        servers[index].busyTime += time - servers[index].time","        if len(waitBuffer) != 0:","            waitClient = waitBuffer.pop(0)","            servers[index].idle = False","            servers[index].time = time","","","# ******************************************************************************","# the \"main\" of the simulation","# ******************************************************************************","","random.seed(42)","","data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)","","# the simulation time","time = 0","","# the list of events in the form: (time, type)","FES = PriorityQueue()","# Initialize servers","servers = []","for i in range(serverNumber):","    servers.append(Server())","","# schedule the first arrival at t=0","FES.put((0, \"arrival\"))","","# simulate until the simulated time reaches a constant","while time < SIM_TIME:","    (time, event_type) = FES.get()","    if BusyServer:","        data.busyTime += time - data.oldT","    if event_type == \"arrival\":","        arrival(time, FES, MMm)","","    elif event_type == \"departure\":","        departure(time, FES, MMm)","","lam = 1/ARRIVAL","mu = 1/(SERVICE)#*serverNumber)","first = 0","for i in range (0,serverNumber):","    first += pow(lam/mu,i)/factorial(i)","second = (pow(lam/mu,serverNumber)/factorial(serverNumber))*(1/(1-(SERVICE/ARRIVAL)))","#second = (((pow(lam/(mu),serverNumber))/(1- (lam/(mu))))*(pow(serverNumber, serverNumber)/factorial(serverNumber)))","pi0 = 1/(first+second)","","print(\"SERVICE\",SERVICE)","print(\"ARRIVAL\",ARRIVAL)","print(\"lam\", lam)","print(\"mu\", mu)","print(\"first\", first)","print(\"second\", second)","print(\"pi0\", pi0)","","#Nw = (pi0*pow(lam/mu,serverNumber)*(SERVICE/ARRIVAL))/(factorial(serverNumber)*pow(1-(SERVICE/ARRIVAL),2))","pim = pi0*1/factorial(serverNumber)*pow(lam/mu,serverNumber)","Nw = (lam*mu*pim)/pow(mu-lam,2)","Tw = (mu*pim)/pow(mu-lam,2)","","# print output data","print(\"MEASUREMENTS \\n\\nNo. of users in the queue:\", users, \"\\nNo. of arrivals =\",","      data.arr, \"- No. of departures =\", data.dep, \"Ergodicity condition: \", lam<(mu))","","print(\"Load: \", SERVICE / ARRIVAL)","print(\"\\nArrival rate: \", data.arr / time, \" - Departure rate: \", data.dep / time)","print(\"Actual queue size: \", len(MMm))","","#print(\"Average queuing delay (all the system): \", data.delay / data.dep)","#print(\"Average time spent in the queue E[T]: \", 1 /(serverNumber*mu - lam)) no","print(\"\\nAverage number of users, E[N]: \", data.ut / time)","print(\"Average number of users, E[N] formula: \", lam*((Nw/lam)+1/mu))","#print(\"Average number of users, E[N] formula: \", Nw+lam/mu)","","print(\"Average delay E[Tw+Ts]: \", data.delay / data.dep)","print(\"Average time in the system, E[T] formula: \", Tw+1/mu)","","print(\"Average waiting in queue E[Tw] over all packets: \", data.waitDel / data.dep)","#print(\"Average waiting in queue E[Tw], formula: \", Nw/lam)","print(\"Average waiting in queue E[Tw], formula: \", Tw)#coincidono","if countQ != 0:","    print(\"Average waiting of packets in queue, E[Tw]: \", data.waitDel / countQ)","print(\"Average number of customers waiting in line, E[Nw] formula: \", Nw)","print(\"Average number of user in queue, E[Nw]: \", data.utBuffer / time)","#print(\"Average number of user in queue, E[Nw]: \", countQ / time)","","print(\"E[Ts], formula: \", 1/(mu))","print(\"E[Ts]: \", data.delay / data.dep - data.waitDel / data.dep)","print(\"Dropped packets: \", nDropped)","print(\"Loss probability: \", nDropped / data.arr)","","print(\"Probability that no customers are in the system: \", pi0)","","# PLot distribution","x = data.delayDistr","plt.hist(x, bins=100)  # It's an exponential","plt.xlabel('Delay')","plt.show()","","for server in servers:","    print(\"Busy time server: \", server.busyTime)","if len(MMm) > 0:","    print(\"Arrival time of the last element in the queue:\", MMm[len(MMm) - 1].arrival_time)",""],"id":4},{"start":{"row":0,"column":0},"end":{"row":277,"column":10},"action":"insert","lines":["#!/usr/bin/python3","","import random","from queue import Queue, PriorityQueue","import matplotlib.pyplot as plt","","# ******************************************************************************","# Constants","# ******************************************************************************","transmNumber = 1","serverNumber = 5","LOAD = 0.33","SERVICE = 10.0  # av service time","mu = 1/SERVICE","lam = (LOAD*mu*serverNumber)/transmNumber","#lam = 0.05","ARRIVAL = 1/lam","#ARRIVAL = 1/(LOAD*(1/SERVICE)*serverNumber)","#LOAD = transmNumber*lam/mu","LOAD = (transmNumber*lam)/(mu*serverNumber)","print('LOAD_def', LOAD)","TYPE1 = 1","c = 0","SIM_TIME = 500000","","arrivals = 0","users = 0","BusyServer = False  # True: server is currently busy; False: server is currently idle","","MMm = []","waitBuffer = []","countQ = 0","maxSize = 50","nDropped = 0","","# ******************************************************************************","# To take the measurements","# ******************************************************************************","class Measure:","    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel, NAveraegUserBuff,","                 BusyTime):","        self.arr = Narr","        self.dep = Ndep","        self.ut = NAveraegUser","        self.oldT = OldTimeEvent","        self.delay = AverageDelay","        self.delayDistr = DelayDistr","        self.waitDel = WaitDel","        self.utBuffer = NAveraegUserBuff","        self.busyTime = BusyTime","","","# ******************************************************************************","# Client","# ******************************************************************************","class Client:","    def __init__(self, type, arrival_time):","        self.type = type","        self.arrival_time = arrival_time","","# ******************************************************************************","# Server","# ******************************************************************************","class Server(object):","    # constructor","    def __init__(self):","        # whether the server is idle or not","        self.idle = True","        self.time = 0","        self.busyTime = 0","","# ******************************************************************************","","def freeServer():","    global servers","    free = []","    for i in range(serverNumber):","        if servers[i].idle == True:","            free.append(i)","    return free","","def busyServer():","    global servers","    busy = []","    for i in range(serverNumber):","        if servers[i].idle == False:","            busy.append(i)","    return busy","","# arrivals *********************************************************************","def arrival(time, FES, queue):","    global users","    global countQ","    global BusyServer","    global nDropped","    global c","    global servers","    # print(\"Arrival no. \",data.arr+1,\" at time \",time,\" with \",users,\" users\" )","","    # cumulate statistics","    data.arr += 1","    data.ut += users * (time - data.oldT)","    data.oldT = time","","    # sample the time until the next event","    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)","","    # schedule the next arrival","    FES.put((time + inter_arrival, \"arrival\"))","","    users += 1","","    # create a record for the client","    client = Client(TYPE1, time)","","    # insert the record in the queue","    queue.append(client)","","    # if the server is idle start the service","    if users <= serverNumber:","        BusyServer = True","        # sample the service time","        service_time = random.expovariate(1 / SERVICE)","        # service_time = 1 + random.uniform(0, SEVICE_TIME)","","        # schedule when the client will finish the server","        FES.put((time + service_time, \"departure\"))","        free = freeServer()","        ix = random.choice(free)","        index = random.randrange(len(free))  # select random server","        # print(ix)","        # print(free)","        servers[free[index]].idle = False","        servers[free[index]].time = time","    else:","        BusyServer = True","        if len(waitBuffer) <= maxSize:","            waitBuffer.append(client)","        else:","            queue.pop(0)","            users -= 1","            nDropped += 1","","","# ******************************************************************************","# def enterFromQueue():","#     global servers","#     if len(waitBuffer) != 0:","#         waitClient = waitBuffer.pop(0)","#         servers[index].idle = False","#         servers[free[index]].time = time","","# departures *******************************************************************","def departure(time, FES, queue):","    global users","    global BusyServer","    global countQ","    global servers","    global c","    # print(\"Departure no. \",data.dep+1,\" at time \",time,\" with \",users,\" users\" )","","    # get the first element from the queue","    if len(queue) > 0:","        client = queue.pop(0)","    else:","        return","        # cumulate statistics","    data.dep += 1","    data.ut += users * (time - data.oldT)","    data.utBuffer += len(waitBuffer) * (time - data.oldT)","    data.oldT = time","    # do whatever we need to do when clients go away","","    data.delay += (time - client.arrival_time)","    data.delayDistr.append(time - client.arrival_time)  # record the queing delay","    users -= 1","","    busy = busyServer()","    index = random.choice(busy)","    # index = random.randrange(len(busy)) # select random server","    servers[index].idle = True","    servers[index].busyTime += time - servers[index].time","","    # see whether there are more clients to in the line","    if users >= serverNumber:","        # users -=1","        # Liberate buffer","        BusyServer = True","","        # sample the service time","        service_time = random.expovariate(1 / SERVICE)","        c += 1","        # schedule when the client will finish the server","        FES.put((time + service_time, \"departure\"))","","        # if len(waitBuffer) != 0:","        # Get waiting time in line","","        data.waitDel += time - waitBuffer[0].arrival_time","","        countQ += 1","        waitClient = waitBuffer.pop(0)","        servers[index].idle = False","        servers[index].time = time","","","# ******************************************************************************","# the \"main\" of the simulation","# ******************************************************************************","","random.seed(42)","","data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)","","# the simulation time","time = 0","","# the list of events in the form: (time, type)","FES = PriorityQueue()","# Initialize servers","servers = []","for i in range(serverNumber):","    servers.append(Server())","","# schedule the first arrival at t=0","FES.put((0, \"arrival\"))","","# simulate until the simulated time reaches a constant","while time < SIM_TIME:","    (time, event_type) = FES.get()","    if BusyServer:","        data.busyTime += time - data.oldT","    if event_type == \"arrival\":","        arrival(time, FES, MMm)","","    elif event_type == \"departure\":","        departure(time, FES, MMm)","","    # print(users)","","# print output data","print(\"MEASUREMENTS \\n\\nNo. of users in the queue:\", users, \"\\nNo. of arrivals =\",","      data.arr, \"- No. of departures =\", data.dep)","","#print(\"Load: \", lam / (serverNumber*mu))","#print(\"Load: \", SERVICE / ARRIVAL)","print(\"Load: \", transmNumber*lam/(serverNumber*mu))","print(\"\\nArrival rate: \", data.arr / time, \" - Departure rate: \", data.dep / time)","","print(\"\\nAverage number of users: \", data.ut / time)","","print(\"Average delay: \", data.delay / data.dep)","print(\"Actual queue size: \", len(MMm))","","print(\"Average waiting time in queue: \", data.waitDel / data.dep)","","if countQ != 0:","    print(\"Average waiting time in queue of packets in queue: \", data.waitDel / countQ)","print(\"Average number of user in waiting line: \", data.utBuffer / time)","print(\"Busy time server: \", data.busyTime)","print(\"Dropped packets: \", nDropped)","print(\"Loss probability: \", nDropped / data.arr)","","# PLot distribution","# x = data.delayDistr","# plt.hist(x,bins=100)    # It's an exponential","# plt.xlabel('Delay')","# plt.show()","","","for server in servers:","    print(\"server busy time: \", server.busyTime)","if len(MMm) > 0:","    print(\"Arrival time of the last element in the queue:\", MMm[len(MMm) - 1].arrival_time)","","# p =","# print([x for x in data.delayDistr if x > 100])","# print(c)"]}],[{"start":{"row":17,"column":0},"end":{"row":18,"column":27},"action":"remove","lines":["#ARRIVAL = 1/(LOAD*(1/SERVICE)*serverNumber)","#LOAD = transmNumber*lam/mu"],"id":5}],[{"start":{"row":15,"column":0},"end":{"row":15,"column":11},"action":"remove","lines":["#lam = 0.05"],"id":6},{"start":{"row":14,"column":41},"end":{"row":15,"column":0},"action":"remove","lines":["",""]}],[{"start":{"row":15,"column":15},"end":{"row":16,"column":0},"action":"remove","lines":["",""],"id":7}],[{"start":{"row":120,"column":0},"end":{"row":120,"column":59},"action":"remove","lines":["        # service_time = 1 + random.uniform(0, SEVICE_TIME)"],"id":8},{"start":{"row":119,"column":54},"end":{"row":120,"column":0},"action":"remove","lines":["",""]}],[{"start":{"row":126,"column":0},"end":{"row":127,"column":21},"action":"remove","lines":["        # print(ix)","        # print(free)"],"id":9}],[{"start":{"row":169,"column":29},"end":{"row":170,"column":19},"action":"remove","lines":["","        # users -=1"],"id":10,"ignore":true}],[{"start":{"row":177,"column":51},"end":{"row":180,"column":34},"action":"remove","lines":["","","        # if len(waitBuffer) != 0:","        # Get waiting time in line"],"id":11,"ignore":true}],[{"start":{"row":218,"column":0},"end":{"row":219,"column":18},"action":"remove","lines":["","    # print(users)"],"id":12,"ignore":true}],[{"start":{"row":217,"column":33},"end":{"row":218,"column":0},"action":"remove","lines":["",""],"id":13,"ignore":true}],[{"start":{"row":241,"column":0},"end":{"row":247,"column":0},"action":"remove","lines":["","# PLot distribution","# x = data.delayDistr","# plt.hist(x,bins=100)    # It's an exponential","# plt.xlabel('Delay')","# plt.show()",""],"id":14,"ignore":true}],[{"start":{"row":247,"column":0},"end":{"row":250,"column":10},"action":"remove","lines":["","# p =","# print([x for x in data.delayDistr if x > 100])","# print(c)"],"id":15,"ignore":true}],[{"start":{"row":222,"column":0},"end":{"row":224,"column":35},"action":"remove","lines":["","#print(\"Load: \", lam / (serverNumber*mu))","#print(\"Load: \", SERVICE / ARRIVAL)"],"id":16}]]},"ace":{"folds":[],"scrolltop":0.5,"scrollleft":0,"selection":{"start":{"row":18,"column":9},"end":{"row":18,"column":9},"isBackwards":false},"options":{"guessTabSize":true,"useWrapMode":false,"wrapToView":true},"firstLineState":0},"hash":"a387ba340dc036eddc1e22d2611fdd8d949d20e7","timestamp":1595574723821}