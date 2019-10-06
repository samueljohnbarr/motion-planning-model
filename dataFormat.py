import math
import sys
import numpy as np
from sklearn.model_selection import glorot_uniform
from sklearn.preprocessing import normalize

"""
   Takes in list components and converts to numpy arrays,
   normalizes input data, partitions data into training and
   testing sets, and expands dimensionality of resulting lists.
   Resulting lists are ready to serve as input to the model.
"""
def format(lidar, targets, tvRv):
    #Convert to numpy lists
    npLidar = np.array(lidar)
    npTargets = np.array(targets)
    npTvRv = np.aray(tvRv)

    #Normalize data (L2 normalization)
    npLidar = normalize(npLidar, norm='l2')
    npTargets = normalize(npTargets, norm='l2')

    #Partition data into training and testing sets
    lTrain, lTest, tTrain, tTest, vTrain, vTest = train_test_split( \
            npLidar, npTargets, npTvRv, test_size=0.25, random_state=42)

    #Expand dimensionality of input data
    a = 1
    lTrain = np.expand_dims(lTrain, axis=a)
    lTest = np.expand_dims(lTest, axis=a)
    tTrain = np.expand_dims(tTrain, axis=a)
    tTest = np.expand_dims(tTest, axis=a)
    vTrain = np.expand_dims(vTrain, axis=a)
    vTest = np.expand_dism(vTest, axis=a)

    return lTrain, lTest, tTrain, tTest, vTrain, vTest


"""
   Calculates distance and angle to goal at every datapoint
   using a 2d list of x & y positions
"""
def calcTargetData(xyList):
    targetList = []
    for i in range(len(xyList)):
        targetElement = []
        R_x = 0
        R_y = 0
        #Create vectors with each pair of points and accumulate x & y's
        for j in range(i, len(xyList)-1, 1):
            A_x = xyList[j+1][0] - xyList[j][0]
            A_y = xyList[j+1][1] - xyList[j][1]
            R_x += A_x
            R_y += A_y
    
        #Determine overall angle accross all vectors
        targetElement.append(math.atan2(R_y,R_x))
        #Determine distance
        targetElement.append(math.sqrt(R_x**2 + R_y**2))

        #Add to targetList
        targetList.append(targetElement)

    return targetList


"""
   This is not used.
   Mini-batches a 2d list 'l'
   Pads with zeros if batch_size does not divide list evenly
   @return minibatched 3d list
"""
def batch(l, batch_size): 
    ans = []
    batch = []
    for i in range(0, len(l), batch_size):
        batch = []
        for j in range(i, i+batch_size):
            if (j < len(l)):
                batch.append(l[j])
            else:
                batch.append([0]*360)

        ans.append(batch)
    return ans

       

