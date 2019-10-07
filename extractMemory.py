import sys
import os


"""
   Saves entire set of data to file
   Any existing file with same name will be overwritten
   @param fileName
   @param listData to save
   @param numPoints number of lists to save
"""
def saveListData(fileName, listData, numPoints):
    count = 1
    f = open(fileName, "w+")
    for i in range(numPoints-1):
        for j in listData[i]:
            f.write("%f\n" % j)
        f.write("\n")
        count = count + 1
    f.close()


"""
   Reads in data from a single extracted file
   Returns a 2d list of extracted data
   @param fileName - should include full path
   @return 2d list of data
"""
def readFileData(fileName):
    readList = []
    sampleDelimiter = '\n'
    f = open(fileName, "r")
    dataPoint = []
    for line in f:
        if(line == sampleDelimeter):
            readList.append(dataPoint)
            dataPoint = []
        else:
            dataPoint.append(float(line.strip(sampleDelimiter)))
    f.close()
    return readList


"""
   Saves extracted lists into respective files in its own set folder.
   Creates directories if none are found.

   @param setName of the dataset - this will be the name of the folder
   @param scans list of lidar scans
   @param targets list of targets
   @param numPoints number of points in the set
"""
def saveExtractedSet(setName, scans, targets, tvRv, numPoints):
    filePath = './extractedData/'
    #Create directory path if none exists
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    filePath += setName + '/'
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    filePath += '/' + setName

    if numPoints > len(tvRv):
        print('*WARNING: Number of lidar scans & number of odometer readings differ.')
        print('          LidarScanLength:', numPoints, '| OdomScanLength: ', len(tvRv))
        print('          Verify parameters are correct.  Truncating lengths...')
        numPoints = len(tvRv)
     
    #Save Lists into respective files
    saveListData(filePath + 'LidarScans.txt', scans, numPoints)
    saveListData(filePath + 'Targets.txt', targets, numPoints)
    saveListData(filePath + 'TvRv.txt', tvRv, numPoints)


"""
   Reads from extractedData folder to build master lists
   of data
   @return ordered lidar scans, target data, velocity vector lists,
           and a count of how many datapoints were retrieved
"""
def readExtractedData():
    lidar = []
    targets = []
    tvRv = []
    numPoints = 0
    for dirpath, dirs, files in os.walk('./extractedData/'):
        for fname in files:
            #Grab the set name
            setName = dirpath.split('/')[-1]
            #Grab the type of data in the file
            ltype = fname.split(setName)[1].split('.txt')[0]
            data = readFileData(dirpath + '/' + fname)
            if ltype == 'LidarScans':
                lidar += data
                numPoints += len(data)
            elif ltype == 'Targets':
                targets += data
            elif ltype == 'TvRv':
                tvRv += data

    return lidar, targets, tvRv, numPoints

