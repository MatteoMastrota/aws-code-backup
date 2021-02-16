{"changed":true,"filter":false,"title":"MM1.py","tooltip":"/management/MM1.py","value":"#!/usr/bin/python3\n\nimport random\nfrom queue import Queue, PriorityQueue\nimport matplotlib.pyplot as plt\n\n# ******************************************************************************\n# Constants\n# ******************************************************************************\n#LOAD = 0.85\nSERVICE = 10.0  # av service time\n#ARRIVAL = SERVICE / LOAD  # av inter-arrival time\nARRIVAL = 10.5\nLOAD = SERVICE/ARRIVAL\nTYPE1 = 1\n\nSIM_TIME = 500000\n\narrivals = 0\nusers = 0\nBusyServer = False  # True: server is currently busy; False: server is currently idle\n\nMM1 = []\nwaitBuffer = []\ncountQ = 0\nnDropped = 0\n\n\n# ******************************************************************************\n# To take the measurements\n# ******************************************************************************\nclass Measure:\n    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel, NAveraegUserBuff,\n                 BusyTime):\n        self.arr = Narr\n        self.dep = Ndep\n        self.ut = NAveraegUser\n        self.oldT = OldTimeEvent\n        self.delay = AverageDelay\n        self.delayDistr = DelayDistr\n        self.waitDel = WaitDel\n        self.utBuffer = NAveraegUserBuff\n        self.busyTime = BusyTime\n\n\n# ******************************************************************************\n# Client\n# ******************************************************************************\nclass Client:\n    def __init__(self, type, arrival_time):\n        self.type = type\n        self.arrival_time = arrival_time\n\n\n# ******************************************************************************\n# Server\n# ******************************************************************************\nclass Server(object):\n\n    # constructor\n    def __init__(self):\n        # whether the server is idle or not\n        self.idle = True\n\n\n# ******************************************************************************\n\n# arrivals *********************************************************************\ndef arrival(time, FES, queue):\n    global users\n    global countQ\n    global BusyServer\n    global nDropped\n    global maxSize\n    # print(\"Arrival no. \",data.arr+1,\" at time \",time,\" with \",users,\" users\" )\n\n    # cumulate statistics\n    data.arr += 1\n    data.ut += users * (time - data.oldT)\n    data.oldT = time\n\n    # sample the time until the next event\n    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)\n\n    # schedule the next arrival\n    FES.put((time + inter_arrival, \"arrival\"))\n\n    users += 1\n\n    # create a record for the client\n    client = Client(TYPE1, time)\n\n    # insert the record in the queue\n    queue.append(client)\n\n    # if the server is idle start the service\n    if users == 1:\n        BusyServer = True\n        # sample the service time\n        service_time = random.expovariate(1.0 / SERVICE)\n        # service_time = 1 + random.uniform(0, SEVICE_TIME)\n\n        # schedule when the client will finish the server\n        FES.put((time + service_time, \"departure\"))\n    else:\n        #BusyServer = True\n        if len(waitBuffer) < maxSize:\n            countQ += 1\n            waitBuffer.append(client)\n            #data.utBuffer += len(waitBuffer) * (time - data.oldT)\n        else:\n            queue.pop(0)\n            users -= 1\n            nDropped += 1\n\n\n# ******************************************************************************\n\n# departures *******************************************************************\ndef departure(time, FES, queue):\n    global users\n    global BusyServer\n    # print(\"Departure no. \",data.dep+1,\" at time \",time,\" with \",users,\" users\" )\n\n    # cumulate statistics\n    data.dep += 1\n    data.ut += users * (time - data.oldT)\n    data.utBuffer += len(waitBuffer) * (time - data.oldT)\n    data.oldT = time\n\n    # get the first element from the queue\n    client = queue.pop(0)\n\n    # do whatever we need to do when clients go away\n\n    data.delay += (time - client.arrival_time)\n    data.delayDistr.append(time - client.arrival_time)  # record the queing delay\n    users -= 1\n\n    # see whether there are more clients to serve in the line\n    if users > 0:\n        # Liberate buffer\n        BusyServer = True\n        waitBuffer.pop(0)\n        # Get waiting time in line\n        data.waitDel += time - queue[0].arrival_time\n        # sample the service time\n        service_time = random.expovariate(1.0 / SERVICE)\n\n        # schedule when the client will finish the server\n        FES.put((time + service_time, \"departure\"))\n    else:\n        BusyServer = False\n\n\n# ******************************************************************************\n# the \"main\" of the simulation\n# ******************************************************************************\ndef main():\n    global data\n    global arrivals\n    global users\n    global BusyServer  # True: server is currently busy; False: server is currently idle\n\n    global MM1\n    global waitBuffer\n    global countQ\n    global maxSize\n    global nDropped\n\n    random.seed(42)\n    arrivals = 0\n    users = 0\n    BusyServer = False  # True: server is currently busy; False: server is currently idle\n\n    MM1 = []\n    waitBuffer = []\n    countQ = 0\n    nDropped = 0\n    data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)\n\n    # the simulation time\n    time = 0\n\n    # the list of events in the form: (time, type)\n    FES = PriorityQueue()\n\n    # schedule the first arrival at t=0\n    FES.put((0, \"arrival\"))\n\n    # simulate until the simulated time reaches a constant\n    while time < SIM_TIME:\n        (time, event_type) = FES.get()\n        if BusyServer:\n            data.busyTime += time - data.oldT\n        if event_type == \"arrival\":\n            arrival(time, FES, MM1)\n\n        elif event_type == \"departure\":\n            departure(time, FES, MM1)\n\n    # print output data\n    lam = 1/ARRIVAL\n    mu = 1/SERVICE\n    rho = SERVICE/ARRIVAL\n    pi0 = (1-rho)/(1-pow(rho,maxSize+1))\n\n    print(\"ARRIVAL: \", ARRIVAL)\n    print(\"SERVICE: \", SERVICE)\n    print(\"lamda: \", lam)\n    print(\"mu:\", mu)\n    print(\"MEASUREMENTS \\n\\nNo. of users in the queue:\", users, \"\\nNo. of arrivals =\",\n          data.arr, \"- No. of departures =\", data.dep, \"Ergodicity condition: \", lam<mu)\n\n    print(\"Load: \", SERVICE / ARRIVAL)\n    print(\"\\nArrival rate: \", data.arr / time, \" - Departure rate: \", data.dep / time)\n\n    print(\"\\nAverage number of users E[N]: \", data.ut / time)\n    #    print(\"Average number of users in the queue, formula E[N]: \", pow(LOAD,2)/(1-LOAD))\n\n    print(\"Average delay, E[Tw+Ts]: \", data.delay/data.dep) #includo anche tempo di servizio\n    #print(\"Tentativo Tw:\", (data.delay/data.dep)-(1/mu))\n    print(\"Actual queue size: \", len(MM1))\n    print(\"Average time spent waiting in queue E[Tw+Ts], formula: \", 1/(mu-lam))\n    print(\"Average number of customer in the system E[N], Little's law formula: \", lam*(1/(mu-lam)))\n    if countQ > 0:\n        print(\"Average waiting in queue of packets in queue E[Tw]: \", data.waitDel/countQ)#something wrong\n    print(\"Average waiting delay over all packets: \", data.waitDel/data.dep)\n    print(\"Average time spent in the waiting line E[Tw], formula: \", rho*(1/(mu - lam)))\n    # print(\"\\nAverage buffer occupancy: \", data.waitPackets / time)\n    print(\"Average number of user in queue E[Nw]: \", data.utBuffer/time)\n    print(\"Average number of users in the waiting line E[Nw], formula: \", rho*(lam/(mu-lam)))\n    print(\"Average number of users in service E[Ns]: \", data.busyTime / time)\n    print(\"Average number of users in the waiting line E[Ns], formula: \", lam/mu)\n\n    print(\"Busy server probability: \", rho)\n\n    print(\"Busy time server: \", data.busyTime)\n    print(\"Dropped packets: \", nDropped)\n    print(\"Loss probability: \", nDropped / data.arr)\n\n    print(\"Loss probability (formula): \", ((1 - rho) / (1 - pow(rho, maxSize + 1))) * pow(rho, maxSize))\n\n    if len(MM1) > 0:\n        print(\"Arrival time of the last element in the queue:\", MM1[len(MM1) - 1].arrival_time)\n    # PLot distribution\n    # x = data.delayDistr\n    # plt.hist(x,bins=100)    # It's an exponential\n    # plt.xlabel('Delay')\n    # plt.show()\n\n    return nDropped / data.arr\n\n\nif __name__ == '__main__':\n    global maxSize\n    maxSize = 3\n    main()","undoManager":{"mark":11,"position":12,"stack":[[{"start":{"row":0,"column":0},"end":{"row":257,"column":10},"action":"insert","lines":["#!/usr/bin/python3","","import random","from queue import Queue, PriorityQueue","import matplotlib.pyplot as plt","","# ******************************************************************************","# Constants","# ******************************************************************************","#LOAD = 0.85","SERVICE = 10.0  # av service time","#ARRIVAL = SERVICE / LOAD  # av inter-arrival time","ARRIVAL = 11.76","LOAD = SERVICE/ARRIVAL","TYPE1 = 1","","SIM_TIME = 500000","","arrivals = 0","users = 0","BusyServer = False  # True: server is currently busy; False: server is currently idle","","MM1 = []","waitBuffer = []","countQ = 0","nDropped = 0","","","# ******************************************************************************","# To take the measurements","# ******************************************************************************","class Measure:","    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, DelayDistr, WaitDel, NAveraegUserBuff,","                 BusyTime):","        self.arr = Narr","        self.dep = Ndep","        self.ut = NAveraegUser","        self.oldT = OldTimeEvent","        self.delay = AverageDelay","        self.delayDistr = DelayDistr","        self.waitDel = WaitDel","        self.utBuffer = NAveraegUserBuff","        self.busyTime = BusyTime","","","# ******************************************************************************","# Client","# ******************************************************************************","class Client:","    def __init__(self, type, arrival_time):","        self.type = type","        self.arrival_time = arrival_time","","","# ******************************************************************************","# Server","# ******************************************************************************","class Server(object):","","    # constructor","    def __init__(self):","        # whether the server is idle or not","        self.idle = True","","","# ******************************************************************************","","# arrivals *********************************************************************","def arrival(time, FES, queue):","    global users","    global countQ","    global BusyServer","    global nDropped","    global maxSize","    # print(\"Arrival no. \",data.arr+1,\" at time \",time,\" with \",users,\" users\" )","","    # cumulate statistics","    data.arr += 1","    data.ut += users * (time - data.oldT)","    data.oldT = time","","    # sample the time until the next event","    inter_arrival = random.expovariate(lambd=1.0 / ARRIVAL)","","    # schedule the next arrival","    FES.put((time + inter_arrival, \"arrival\"))","","    users += 1","","    # create a record for the client","    client = Client(TYPE1, time)","","    # insert the record in the queue","    queue.append(client)","","    # if the server is idle start the service","    if users == 1:","        BusyServer = True","        # sample the service time","        service_time = random.expovariate(1.0 / SERVICE)","        # service_time = 1 + random.uniform(0, SEVICE_TIME)","","        # schedule when the client will finish the server","        FES.put((time + service_time, \"departure\"))","    else:","        #BusyServer = True","        if len(waitBuffer) < maxSize:","            countQ += 1","            waitBuffer.append(client)","            #data.utBuffer += len(waitBuffer) * (time - data.oldT)","        else:","            queue.pop(0)","            users -= 1","            nDropped += 1","","","# ******************************************************************************","","# departures *******************************************************************","def departure(time, FES, queue):","    global users","    global BusyServer","    # print(\"Departure no. \",data.dep+1,\" at time \",time,\" with \",users,\" users\" )","","    # cumulate statistics","    data.dep += 1","    data.ut += users * (time - data.oldT)","    data.utBuffer += len(waitBuffer) * (time - data.oldT)","    data.oldT = time","","    # get the first element from the queue","    client = queue.pop(0)","","    # do whatever we need to do when clients go away","","    data.delay += (time - client.arrival_time)","    data.delayDistr.append(time - client.arrival_time)  # record the queing delay","    users -= 1","","    # see whether there are more clients to serve in the line","    if users > 0:","        # Liberate buffer","        BusyServer = True","        waitBuffer.pop(0)","        # Get waiting time in line","        data.waitDel += time - queue[0].arrival_time","        # sample the service time","        service_time = random.expovariate(1.0 / SERVICE)","","        # schedule when the client will finish the server","        FES.put((time + service_time, \"departure\"))","    else:","        BusyServer = False","","","# ******************************************************************************","# the \"main\" of the simulation","# ******************************************************************************","def main():","    global data","    global arrivals","    global users","    global BusyServer  # True: server is currently busy; False: server is currently idle","","    global MM1","    global waitBuffer","    global countQ","    global maxSize","    global nDropped","","    random.seed(42)","    arrivals = 0","    users = 0","    BusyServer = False  # True: server is currently busy; False: server is currently idle","","    MM1 = []","    waitBuffer = []","    countQ = 0","    nDropped = 0","    data = Measure(0, 0, 0, 0, 0, [], 0, 0, 0)","","    # the simulation time","    time = 0","","    # the list of events in the form: (time, type)","    FES = PriorityQueue()","","    # schedule the first arrival at t=0","    FES.put((0, \"arrival\"))","","    # simulate until the simulated time reaches a constant","    while time < SIM_TIME:","        (time, event_type) = FES.get()","        if BusyServer:","            data.busyTime += time - data.oldT","        if event_type == \"arrival\":","            arrival(time, FES, MM1)","","        elif event_type == \"departure\":","            departure(time, FES, MM1)","","    # print output data","    lam = 1/ARRIVAL","    mu = 1/SERVICE","    rho = SERVICE/ARRIVAL","    pi0 = (1-rho)/(1-pow(rho,maxSize+1))","","    print(\"ARRIVAL: \", ARRIVAL)","    print(\"SERVICE: \", SERVICE)","    print(\"lamda: \", lam)","    print(\"mu:\", mu)","    print(\"MEASUREMENTS \\n\\nNo. of users in the queue:\", users, \"\\nNo. of arrivals =\",","          data.arr, \"- No. of departures =\", data.dep, \"Ergodicity condition: \", lam<mu)","","    print(\"Load: \", SERVICE / ARRIVAL)","    print(\"\\nArrival rate: \", data.arr / time, \" - Departure rate: \", data.dep / time)","","    print(\"\\nAverage number of users E[N]: \", data.ut / time)","    #    print(\"Average number of users in the queue, formula E[N]: \", pow(LOAD,2)/(1-LOAD))","","    print(\"Average delay, E[Tw+Ts]: \", data.delay/data.dep) #includo anche tempo di servizio","    #print(\"Tentativo Tw:\", (data.delay/data.dep)-(1/mu))","    print(\"Actual queue size: \", len(MM1))","    print(\"Average time spent waiting in queue E[Tw+Ts], formula: \", 1/(mu-lam))","    print(\"Average number of customer in the system E[N], Little's law formula: \", lam*(1/(mu-lam)))","    if countQ > 0:","        print(\"Average waiting in queue of packets in queue E[Tw]: \", data.waitDel/countQ)#something wrong","    print(\"Average waiting delay over all packets: \", data.waitDel/data.dep)","    print(\"Average time spent in the waiting line E[Tw], formula: \", rho*(1/(mu - lam)))","    # print(\"\\nAverage buffer occupancy: \", data.waitPackets / time)","    print(\"Average number of user in queue E[Nw]: \", data.utBuffer/time)","    print(\"Average number of users in the waiting line E[Nw], formula: \", rho*(lam/(mu-lam)))","    print(\"Average number of users in service E[Ns]: \", data.busyTime / time)","    print(\"Average number of users in the waiting line E[Ns], formula: \", lam/mu)","","    print(\"Busy server probability: \", rho)","","    print(\"Busy time server: \", data.busyTime)","    print(\"Dropped packets: \", nDropped)","    print(\"Loss probability: \", nDropped / data.arr)","","    print(\"Loss probability (formula): \", ((1 - rho) / (1 - pow(rho, maxSize + 1))) * pow(rho, maxSize))","","    if len(MM1) > 0:","        print(\"Arrival time of the last element in the queue:\", MM1[len(MM1) - 1].arrival_time)","    # PLot distribution","    # x = data.delayDistr","    # plt.hist(x,bins=100)    # It's an exponential","    # plt.xlabel('Delay')","    # plt.show()","","    return nDropped / data.arr","","","if __name__ == '__main__':","    global maxSize","    maxSize = 100","    main()"],"id":1}],[{"start":{"row":12,"column":11},"end":{"row":12,"column":12},"action":"remove","lines":["1"],"id":2}],[{"start":{"row":12,"column":11},"end":{"row":12,"column":12},"action":"insert","lines":["0"],"id":3}],[{"start":{"row":12,"column":13},"end":{"row":12,"column":14},"action":"remove","lines":["7"],"id":4},{"start":{"row":12,"column":13},"end":{"row":12,"column":14},"action":"remove","lines":["6"]}],[{"start":{"row":12,"column":13},"end":{"row":12,"column":14},"action":"insert","lines":["5"],"id":5}],[{"start":{"row":256,"column":16},"end":{"row":256,"column":17},"action":"remove","lines":["0"],"id":6},{"start":{"row":256,"column":15},"end":{"row":256,"column":16},"action":"remove","lines":["0"]},{"start":{"row":256,"column":14},"end":{"row":256,"column":15},"action":"remove","lines":["1"]}],[{"start":{"row":256,"column":14},"end":{"row":256,"column":15},"action":"insert","lines":["3"],"id":7}],[{"start":{"row":12,"column":13},"end":{"row":12,"column":14},"action":"remove","lines":["5"],"id":8},{"start":{"row":12,"column":12},"end":{"row":12,"column":13},"action":"remove","lines":["."]},{"start":{"row":12,"column":11},"end":{"row":12,"column":12},"action":"remove","lines":["0"]},{"start":{"row":12,"column":10},"end":{"row":12,"column":11},"action":"remove","lines":["1"]}],[{"start":{"row":12,"column":10},"end":{"row":12,"column":11},"action":"insert","lines":["3"],"id":9},{"start":{"row":12,"column":11},"end":{"row":12,"column":12},"action":"insert","lines":["0"]}],[{"start":{"row":12,"column":11},"end":{"row":12,"column":12},"action":"remove","lines":["0"],"id":10},{"start":{"row":12,"column":10},"end":{"row":12,"column":11},"action":"remove","lines":["3"]}],[{"start":{"row":12,"column":10},"end":{"row":12,"column":11},"action":"insert","lines":["1"],"id":11},{"start":{"row":12,"column":11},"end":{"row":12,"column":12},"action":"insert","lines":["0"]},{"start":{"row":12,"column":12},"end":{"row":12,"column":13},"action":"insert","lines":["."]},{"start":{"row":12,"column":13},"end":{"row":12,"column":14},"action":"insert","lines":["5"]}],[{"start":{"row":231,"column":69},"end":{"row":231,"column":70},"action":"insert","lines":["a"],"id":12},{"start":{"row":231,"column":70},"end":{"row":231,"column":71},"action":"insert","lines":["a"]},{"start":{"row":231,"column":71},"end":{"row":231,"column":72},"action":"insert","lines":["a"]},{"start":{"row":231,"column":72},"end":{"row":231,"column":73},"action":"insert","lines":["a"]},{"start":{"row":231,"column":73},"end":{"row":231,"column":74},"action":"insert","lines":["a"]},{"start":{"row":231,"column":74},"end":{"row":231,"column":75},"action":"insert","lines":["a"]},{"start":{"row":231,"column":75},"end":{"row":231,"column":76},"action":"insert","lines":["a"]},{"start":{"row":231,"column":76},"end":{"row":231,"column":77},"action":"insert","lines":["a"]},{"start":{"row":231,"column":77},"end":{"row":231,"column":78},"action":"insert","lines":["a"]},{"start":{"row":231,"column":78},"end":{"row":231,"column":79},"action":"insert","lines":["a"]},{"start":{"row":231,"column":79},"end":{"row":231,"column":80},"action":"insert","lines":["a"]},{"start":{"row":231,"column":80},"end":{"row":231,"column":81},"action":"insert","lines":["a"]},{"start":{"row":231,"column":81},"end":{"row":231,"column":82},"action":"insert","lines":["a"]},{"start":{"row":231,"column":82},"end":{"row":231,"column":83},"action":"insert","lines":["a"]},{"start":{"row":231,"column":83},"end":{"row":231,"column":84},"action":"insert","lines":["a"]},{"start":{"row":231,"column":84},"end":{"row":231,"column":85},"action":"insert","lines":["a"]},{"start":{"row":231,"column":85},"end":{"row":231,"column":86},"action":"insert","lines":["a"]},{"start":{"row":231,"column":86},"end":{"row":231,"column":87},"action":"insert","lines":["a"]}],[{"start":{"row":231,"column":69},"end":{"row":231,"column":87},"action":"remove","lines":["aaaaaaaaaaaaaaaaaa"],"id":13}]]},"ace":{"folds":[],"scrolltop":3400.5,"scrollleft":0,"selection":{"start":{"row":231,"column":69},"end":{"row":231,"column":69},"isBackwards":false},"options":{"guessTabSize":true,"useWrapMode":false,"wrapToView":true},"firstLineState":{"row":225,"mode":"ace/mode/python"}},"timestamp":1589832671973}