import sys
from datetime import datetime
import numpy

laserStr = 'ROBOTLASER1'

#mit3rdfloorlidar=numpy.zeros(shape=(1,360))
#mit3rdfloorangle=numpy.zeros(shape=(1,1))

#lidar arrays that start at 90 degrees will be ordered to start at 0
def reorder(arr):
    ans = []
    for i in range(180,360):
        ans.append(arr[i])
    for j in range(0,180):
        ans.append(arr[j])
    return ans


def countKeywords(fileName, keyword, numOmit):
    with open(fileName, 'r') as file:
        strFile = file.read()
    count = 1
    j = strFile.find(keyword)
    while (j != -1):
        j = strFile.find(keyword, j+1)
        count = count + 1
    return count-numOmit


"""
  Takes in a list of strings and converts to list of floats
  @param string list to convert
  @param meter to centimeter conversion
"""
def floatify(strList, mToCm):
    floatList = []
    for i in range(len(strList)):
      num = float(strList[i])
      if (mToCm):
          num = num * 100
      floatList.append(num)
    return floatList

def extractLidarScans(fileName, keyword, numOmit, numAfter, numPoints, numPointsCollect):
    scanSet = []
    #Open file and turn into string
    with open(fileName, 'r') as file:
        strFile = file.read()
    j = -1
    count = 1
    #Skip over omitted instances of keyword
    for i in range(numOmit+1):
        j = strFile.find(keyword, j+1)
    #Loop while there are more keywords
    while (j != -1):
        #Cut keyword and preceeding data
        cut = strFile[j:]
        #Cut proceeding data up to laser measurements
        startIndex = cut.find(str(numPoints))
        strValues = cut[startIndex:].split(' ', numAfter+numPointsCollect)[numAfter:numPointsCollect]
        #Convert data to float
        final = floatify(strValues, True)
        scanSet.append(final)
        j = strFile.find(keyword, j+1)
        print('Point #', count, '...', 'KeywordPos:', j)
        count = count + 1
    return scanSet


"""
   extracts and returns array of traslational & rotational velocities
   @param filename of dataset
   @param keyword of where to find Tv and Rv in data
   @param numOmit number of omissions of keyword at start of the dataset
   @param numPoints number of values to grab at each datapoint
"""
def extractTvRv(fileName, keyword, numOmit, numAfter, numPoints):
    tvRvSet = []
    #Open file and turn into string
    with open(fileName, 'r') as file:
        strFile = file.read()
    j = -1
    count = 1
    #Skip over first occurances of keyword
    for i in range(numOmit+1):
        j = strFile.find(keyword, j+1)
    #Loop while there are more keywords
    while (j != -1):
        #Cut keyword and preceeding data
        strValues = strFile[j:].split(' ', numAfter+numPoints)[numAfter:numAfter+numPoints]
        print(strValues)
        final = floatify(strValues, False)
        tvRvSet.append(final)
        j = strFile.find(keyword,j+1)
        print('Point #', count, '...', 'KeywordPos:', j)
        count = count+1
    return tvRvSet
         

"""
   Saves single data point to a file where each line contains a single reading
   Any existing file with same name will be overwritten
   @param dataPoint to save | 0 -> (number of total datapoints)
"""
def saveSingleListData(fileName, listData, dataPoint):
    f = open(fileName, "w+")
    for i in range(len(listData[dataPoint])):
        f.write("%f\n" % listData[dataPoint][i])
    f.close()


"""
   Saves entire set of data to file
   @param fileName to set
   @param numPoints number of lists to save
"""
def saveAllListData(fileName, listData, numPoints):
    count = 1
    f = open(fileName, "w+")
    for i in range(numPoints-1):
        for j in listData[i]:
            f.write("%f\n" % j)
        f.write("\n")
        print('Point', count, 'saved')
        count = count + 1
    f.close()


"""
   Reads in data from an already extracted file
   Returns a 2d list of extracted data
"""
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


"""
   Converts a 2d array to a 1d one
   Used for theta data
"""
def twoDtoOneD(dataList):
    ans = []
    for l in dataList:
        for element in l:
            ans.append(element)

    return ans


def extractMITData():
    #Dataset file
    file1 = 'rawData/mit-csail-3rd-floor-2005-12-17-run4.log'
    
    #Extract data into lists
    mitScans = extractLidarScans(file1, 'ROBOTLASER1', 2, 1, 361, 360)
    mitTvRv = extractTvRv(file1, 'ODOM', 2, 4, 2)
    mitTheta = extractTvRv(file1, 'ODOM', 2, 3, 1)
    mitXy = extractTvRv(file1, 'ODOM', 2, 1, 2)
    numPoints = countKeywords(file1, 'ROBOTLASER1', 2)

    #Save lists in different files
    saveAllListData("extractedData/mitLidarScans.txt", mitScans, numPoints) 
    saveAllListData("extractedData/mitTvRv.txt", mitTvRv, numPoints)
    saveAllListData("extractedData/mitTheta.txt", mitTheta, numPoints)

    print('MIT data extracted and saved')


def extractCarmenData():
    #Dataset file
    file2 = 'rawData/fr-campus-20040714.carmen.log'
    
    #Extract data into lists
    carmenScans = extractLidarScans(file2, 'FLASER', 6, 1, 360, 360)
    carmenTvRv = extractTvRv(file2, 'ODOM', 5, 4, 2)
    carmenTheta = extractTvRv(file2, 'ODOM', 5, 3, 1)
    carmenXy = extractTvRv(file2, 'ODOM', 5, 1, 2)
    numPoints = countKeywords(file2, 'FLASER', 6)

    #Save lists in different files
    saveAllListData("extractedData/carmenLidarScans.txt", carmenScans, numPoints)
    #saveAllListData("extractedData/carmenTvRv.txt", carmenTvRv, numPoints)
    #saveAllListData("extractedData/carmenTheta.txt", carmenTheta, numPoints)
    


"""
   Extracts all relavent data from datasets and seperates them into
   seperate files
"""
def extractAll():
    #Keep all arrays as lists
    #Only when finished should you concatenate all and convert to numpy array
    extractMITData()
    extractCarmenData()

    print('Done.')


def convertToTrainingData(train_data, lidar_list, theta_list):
   train_element = []
   #Iterate through each list
   for scan_index in range(len(lidar_list)):
       #Append each list element at the index to training element
       train_element.append(lidar_list[scan_index])
       train_element.append([theta_list[scan_index]])
       #Append to training data
       train_data.append(train_element)
       train_element = []


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



def calcTargetData(thetaList, xyList):
   targetList = []
   lastAngle = thetaList[len(thetaList)-1]
   lastXy = xyList[len(xyList)-1]

   targetElement = []
   for i in range(len(thetaList)):
       targetElement.append(lastAngle-thetaList[i])
       targetElement.append(math.sqrt((lasyXy[0]-xyList[i])**2 + (lastXy[1]-xyList[i])**2))
       targetList.append(targetElement)
       targetElement = []
   return targetList


def readExtractedData():
   mitLidar = readListData('extractedData/mitLidarScans.txt')
   mitTvRv  = readListData('extractedData/mitTvRv.txt')
   mitTheta = twoDtoOneD(readListData('extractedData/mitTheta.txt'))
   
   carmenLidar = readListData('extractedData/carmenLidarScans.txt')
   carmenTvRv  = readListData('extractedData/carmenTvRv.txt')
   carmenTheta = twoDtoOneD(readListData('extractedData/carmenTheta.txt'))

   training_data = []
   training_labels = []
   convertToTrainingData(training_data, mitLidar, mitTheta)
   convertToTrainingData(training_data, carmenLidar, carmenTheta)
   training_labels = mitTvRv
   training_labels = training_labels + carmenTvRv
   np_training_data = numpy.array(training_data)
   np_training_labels = numpy.array(training_labels)

   return np_training_data, np_training_labels



readExtractedData()

#np_mitScans = numpy.array(mitScans)
#np_mitOdom = numpy.array(mitOdom)

