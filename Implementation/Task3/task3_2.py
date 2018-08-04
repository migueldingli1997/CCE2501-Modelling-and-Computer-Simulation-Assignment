import random
import matplotlib.pyplot as plt
import numpy as np

def graph(x):
    return 5 * (x ** 4) - 8.7 * (x ** 3) + 33 * (x ** 2) + 21 * (x) + 10.8

xValues = np.linspace(0, 5, 10000)
yValues = np.array(list(map(graph, xValues)))

plt.figure()
plt.plot(xValues, yValues, '-b')
plt.xlabel("x")
plt.ylabel("y")
plt.title("Graph of y = 5(x^4) - 8.7(x^3) + 33(x^2) + 21(x) + 10.8")
plt.grid()
plt.show()

##################################################################################

xLimits = [0, 5]
yLimits = [0, graph(5)]
xRange = xLimits[1] - xLimits[0]
yRange = yLimits[1] - yLimits[0]

pointsUnderGraph = []
pointsOverGraph = []

def calcArea(iterations: int, appendToArray: bool) -> float:
    countUnder = 0

    for i in range(iterations):
        point = [random.uniform(xLimits[0], xLimits[1]), random.uniform(yLimits[0], yLimits[1])]
        isUnderGraph = point[1] < graph(point[0])
        countUnder += 1 if isUnderGraph else 0

        if appendToArray:
            if isUnderGraph:
                pointsUnderGraph.append(point)
            else:
                pointsOverGraph.append(point)

    return (countUnder / iterations) * (xRange * yRange)

##################################################################################

area = calcArea(100000, True)
analytical = 3457.125
print("Area after 100,000 iterations: %f" % area)
print("Area achieved analytically:    %f" % analytical)
print("Percentage error:              %f" % np.abs(100 * (analytical - area) / analytical))

np_underGraph = np.array(pointsUnderGraph)
np_overGraph = np.array(pointsOverGraph)

plt.figure()
plt.scatter(np_underGraph[:, 0], np_underGraph[:, 1], c='b', label="Under Graph")
plt.scatter(np_overGraph[:, 0], np_overGraph[:, 1], c='r', label="Over Graph")
plt.title("Plot of Random Points Under and Over the Graph")
plt.legend()
plt.grid()
plt.show()

##################################################################################

N_iters = range(10000, 1000001, 10000)
areaValues = []
print()
for N_iter in N_iters:
    areaValues.append(calcArea(N_iter, False))
    print("Area after %d iterations: %f" % (N_iter, areaValues[-1]))

averageArea = np.mean(areaValues)
print()
print("Average area:                %f" % averageArea)
print("Area achieved analytically:  %f" % analytical)
print("Percentage error:            %f" % np.abs(100 * (analytical - averageArea) / analytical))

plt.figure()
plt.plot(N_iters, areaValues, '-bx')
plt.plot([N_iters[0], N_iters[-1]], [analytical, analytical], '-r')
plt.xlabel("Number of iterations")
plt.ylabel("Area")
plt.title("Plot of Area versus No. of Iterations")
plt.grid()
# plt.show()

##################################################################################

errorValues = list(map(lambda a: 100 * np.abs(a - analytical) / analytical, areaValues))

plt.figure()
plt.plot(N_iters, errorValues, '-bx')
plt.plot([N_iters[0], N_iters[-1]], [1, 1], '-r')
plt.xlabel("Number of iterations")
plt.ylabel("Percentage Error")
plt.title("Plot of Percentage Error versus No. of Iterations")
plt.grid()
plt.show()

minimumIter = 0
for i in reversed(range(len(errorValues))):  # traverse in reverse
    if errorValues[i] > 1:
        minimumIter = N_iters[i+1]  # at i+1 was last for which error was < 1%
        break
print()
print("Minimum number of iterations: %d" % minimumIter)
