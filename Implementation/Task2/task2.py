from scipy import stats
from enum import IntEnum
import matplotlib.pyplot as plt
import time
import numpy as np

def nowStr():
    return time.strftime('%H h, %M min', time.gmtime(NOW))

def timeStr():
    return 'Morning' if morning else 'Evening'

############################################################################################

# CONSTANTS
SERVICETIME = 2         # fixed service time of 2 seconds
LIGHTSCHANGETIME = 30   # fixed lights interval of 30 seconds
TIMELIMIT = 14400       # maximum time of 4 hours (14400 seconds)

class Road(IntEnum):
    A = 0               # Road A
    B = 1               # Road B

class EVT(IntEnum):
    ARRIVAL = 0         # Arrival event
    START_S = 1         # Start service event
    END_S = 2           # End service event
    LIGHTSCHANGE = 3    # Light change event

############################################################################################

def addPlot1Values():
    global plot1
    plot1[0].append(NOW / 3600)     # current time
    plot1[1].append(qLen)           # car count in service node

def addPlot2Values():
    global plot2
    plot2.append(NOW / 3600)        # time of arrival

############################################################################################

def getInterarrivalTime():
    iat = 0
    while iat < 1 or iat > 10:
        iat = (np.random.exponential(2))  # generate iat from exponential distribution
    return iat / stats.norm.pdf(NOW / 3600, loc=iatMeans[road], scale=iatStdevs[road])

def scheduleEvent(eventType, eventTime):
    eventList.append([eventType, eventTime])

def arrival():
    global totalARR, totalIAT, qLen

    # for the next car...
    iat = getInterarrivalTime()
    scheduleEvent(EVT.ARRIVAL, NOW + iat)  # schedule arrival of next car
    totalARR += 1       # 1 more car arrived
    totalIAT += iat     # added to total inter-arrival times

    # for the current car...
    qLen += 1
    if not serverBusy: # schedule service start of current car if server is not busy
        if greenLights:
            scheduleEvent(EVT.START_S, NOW)
        elif qLen == 1:  # if only 1 car, schedule its service to closest lights change
            nextLightChange = next(event[1] for event in eventList if event[0] == EVT.LIGHTSCHANGE)
            scheduleEvent(EVT.START_S, nextLightChange)

    # add plot values and output to file
    addPlot1Values()  # for queue length vs. time plot
    addPlot2Values()  # for time of arrival
    FILE.write('Car arrived.   (QLen: %d) (Time: %s) [Next in %f time]\n' % (qLen, nowStr(), iat))

def startservice():
    global qLen, serverBusy

    qLen -= 1                                    # car left the queue
    serverBusy = True                            # server now busy
    scheduleEvent(EVT.END_S, NOW + SERVICETIME)  # schedule service end of current car

    # add plot values and output to file
    addPlot1Values()  # for queue length vs. time plot
    FILE.write('Service start. (QLen: %d) (Time: %s)\n' % (qLen, nowStr()))

def endservice():
    global serverBusy

    serverBusy = False                      # server now free
    if qLen > 0 and greenLights:
        scheduleEvent(EVT.START_S, NOW)     # schedule next car service

    # add plot values and output to file
    addPlot1Values()  # for queue length vs. time plot
    FILE.write('Service end.   (QLen: %d) (Time: %s)\n' % (qLen, nowStr()))

def lightschange():
    global greenLights
    greenLights = not greenLights
    scheduleEvent(EVT.LIGHTSCHANGE, NOW + LIGHTSCHANGETIME)  # schedule lights change

    # output to file
    FILE.write('Lights change. (QLen: %d) (Time: %s)\n' % (qLen, nowStr()))

############################################################################################

def initialize(theRoad: Road, fileSuffix: str):
    global NOW, eventList, qLen, serverBusy, greenLights, road
    global plot1, plot2, totalARR, totalIAT, FILE

    NOW = 0                         # current time
    eventList = []                  # [eventType, eventTime]
    road = theRoad                  # the road

    qLen = 0                        # length of car queues
    serverBusy = False              # indicates if server is busy; initially idle
    greenLights = (road == Road.A)  # indicates if road is green (T) or red (F)

    plot1 = [[], []]                # values for car count vs. time plot
    plot2 = []                      # values of time of arrivals

    totalARR = 0                    # total arrivals
    totalIAT = 0                    # total inter-arrival time

    # open file to log event details to
    FILE = open('task2_Output_' + fileSuffix + '.txt', 'w')

    scheduleEvent(EVT.ARRIVAL, NOW)  # arrival of 1st car
    scheduleEvent(EVT.LIGHTSCHANGE, NOW + LIGHTSCHANGETIME)  # event for 1st lights change

def runSimulation() -> ([[int], [int]], [float]):
    global NOW, eventList

    # Note: event list contains at least 1 event, a change lights event
    while NOW <= TIMELIMIT or len(eventList) > 1:
        eventList = sorted(eventList, key=lambda x: x[1])      # sort by event time
        firstEvent = eventList.pop(0)                          # get first event
        NOW = firstEvent[1]                                    # update time
        if firstEvent[0] == EVT.ARRIVAL and NOW <= TIMELIMIT:  # no more arrivals after limit
            arrival()  # car arrived
        elif firstEvent[0] == EVT.START_S:
            startservice()  # start car service
        elif firstEvent[0] == EVT.END_S:
            endservice()  # end car service
        elif firstEvent[0] == EVT.LIGHTSCHANGE:
            lightschange()  # lights swap

    # close event details file
    FILE.close()

    # calculations
    arrivalRate = totalARR / totalIAT   # arrival rate
    serviceRate = 1 / SERVICETIME       # service rate
    print('Calculations for Road ' + ('A ' if road == Road.A else 'B ') + '(' + timeStr() + '):')
    print('\tArrival rate: %f' % arrivalRate)
    print('\tService rate: %f' % serviceRate)
    print('\tTraffic intensity: %f' % (arrivalRate / serviceRate))
    print()

    return plot1, plot2

def plots(plt1, plt2):
    # qLen vs. time plot
    plt.figure()
    plt.plot(plt1[0][0], plt1[0][1], '-bo', label='Road A')
    plt.plot(plt1[1][0], plt1[1][1], '-ro', label='Road B')
    plt.ylabel('Number of cars in queue')
    plt.xlabel('Time')
    plt.title('Queue length as a function of time (' + timeStr() + ')')
    plt.legend()
    plt.grid()

    # arrivals vs. time plot
    plt.figure()
    plt.hist(plt2[0], bins=20, range=[0,4], histtype='step', color='blue', label='Road A')
    plt.hist(plt2[1], bins=20, range=[0,4], histtype='step', color='red', label='Road B')
    plt.ylabel('Car arrivals')
    plt.xlabel('Time')
    plt.title('Arrivals (' + timeStr() + ')')
    plt.legend()
    plt.grid()

############################################################################################

def fullSimulationWithPlots(timePeriod: bool, means: [float, float], stdevs: [float, float]):
    global morning, iatMeans, iatStdevs
    morning = timePeriod
    iatMeans = means
    iatStdevs = stdevs

    initialize(Road.A, timeStr() + '_A')             # Initialize
    (plot1_1, plot2_1) = runSimulation()             # Road A
    initialize(Road.B, timeStr() + '_B')             # Initialize
    (plot1_2, plot2_2) = runSimulation()             # Road B
    plots((plot1_1, plot1_2), (plot2_1, plot2_2))    # Plot

fullSimulationWithPlots(True, [2, 2.5], [1, 0.95])   # Morning
fullSimulationWithPlots(False, [2, 1.5], [0.95, 1])  # Evening
plt.show()  # show plots
