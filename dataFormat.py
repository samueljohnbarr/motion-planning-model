import math
import sys
#import numpy

"""
   Returns number of training samples that are extracted
   and are ready for processing
"""
def getNumSamples():
    file1 = 'rawData/mit-csail-3rd-floor-2005-12-17-run4.log'
    file2 = 'rawData/fr-campus-20040714.carmen.log'
    numPoints = countKeywords(file1, 'ROBOTLASER1', 2) 
    numPoints = numPoints + countKeywords(file2, 'FLASER', 6)
    return numPoints


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

       

def readExtractedData():
   mitLidar = readListData('extractedData/mit/mitLidarScans.txt')
   mitTvRv  = readListData('extractedData/mit/mitTvRv.txt')
   mitTargets = readListData('extractedData/mit/mitTargets.txt')
   
   carmenLidar = readListData('extractedData/carmen/carmenLidarScans.txt')
   carmenTvRv  = readListData('extractedData/carmen/carmenTvRv.txt')
   carmenXy = readListData('extractedData/carmen/carmenXy.txt')
   carmenTargets = readListData('extractedData/carmen/carmenTargets.txt')

   print('lidar: ' + str(len(mitLidar)))
   print('tvrv: ' + str(len(mitTvRv)))
   print('targets: ' + str(len(mitTargets)))

   print('lidar: ' + str(len(carmenLidar)))
   print('tvrv: ' + str(len(carmenTvRv)))
   print('xY: ' + str(len(carmenXy)))
   print('targets: ' + str(len(carmenTargets)))

   #lidarTrain = numpy.array(mitLidar + carmenLidar)
   #targetTrain = numpy.array(mitTargets + carmenTargets)
   #velocityLabels = numpy.array(mitTvRv + carmenTvRv)


   #return lidarTrain, targetTrain, velocityLabels

