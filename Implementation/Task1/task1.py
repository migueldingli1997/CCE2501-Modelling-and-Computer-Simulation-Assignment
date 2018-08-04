import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

tLimits = [0, 5]
mu = 0
sigma = 0.75

def lognorm(t):
    return (np.exp(-((np.log(t) - mu) ** 2) / (2 * sigma ** 2))) / (t * sigma * np.sqrt(2 * np.pi))

tValues = np.arange(0.01, 5, 0.01)
yValues = np.array(list(map(lognorm, tValues)))
plt.figure()
plt.plot(tValues, yValues, '-b')
plt.ylabel('y')
plt.xlabel('t')
plt.title("Log-Normal Distribution")
plt.grid()
plt.show()

##############################################################################

M = np.ceil(max(yValues))
print("M = %f" % M)

binRange = tLimits[1] - tLimits[0]
binCount = 100

rand_lognorm = np.zeros(binCount)           # Array of 'binCount' bins
bins = np.linspace(0, binRange, binCount)   # Array of 'binCount' bin limits from 0 to 'binRange'

# Generate uniform random nos. and convert them to a lognormal dist. using accept-reject
def generatePoint():
    u = random.uniform(tLimits[0], tLimits[1])
    v = random.uniform(0, M)
    if v < lognorm(u):
        for j in range(0, len(bins)):
            if u < bins[j]:
                rand_lognorm[j] += 1
                break

for i in range(10000):
    generatePoint()

print(rand_lognorm)

##############################################################################

binWidth = binRange / binCount
area = sum(binWidth * rand_lognorm)

plt.figure()
plt.plot(bins, rand_lognorm / area, 'bo', label="By Von-Neumann Method")
plt.plot(bins, stats.lognorm([sigma],loc=mu).pdf(bins), '-r', label="By Standard Library")
plt.ylabel('Number of counts')
plt.xlabel('X, the log-normally distributed random variable')
plt.title("Probability Density Function")
plt.grid()
plt.legend()
plt.show()
