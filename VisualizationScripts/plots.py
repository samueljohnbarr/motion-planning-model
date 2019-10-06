import numpy as np
import matplotlib.pyplot as plt

def readListData(fileName):
    readList = []
    f = open(fileName, "r")
    dataPoint = []
    for line in f:
        if(line == '\n'):
            readList.append(dataPoint)
            dataPoint = []
        else:
            dataPoint.append(float(line.strip('\n')))
    f.close()
    return readList


def plot(name, vList):
    tv =[]
    rv = []
    x = []
    #Break list into two
    for i in range(len(vList)):
        x.append(i)
        tv.append(vList[i][0])
        rv.append(vList[i][1])

    #Define plot attributes
    colors = ("red", "blue")
    groups = ("translational", "rotational")

    #Create plot
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(x, tv, alpha=0.8, c='red', label='translational')
    ax.plot(x, rv, alpha=0.8, c='blue', label='rotational')

    ax.set_xlabel('Datapoint #')
    ax.set_ylabel('Velocity')

    plt.title(name + ' Translational vs. Rotational Velocities')
    plt.legend(loc=2)
    plt.show()


vList = readListData('extractedData/mitTvRv.txt')
plot('MIT', vList)

#vList = readListData('extractedData/carmenTvRv.txt')
#plot('Carmen', vList)
