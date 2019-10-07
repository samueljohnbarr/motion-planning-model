import math


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


"""
   returns the amount of keywords within a file
   @param fileName of file to count
   @param keyword to count
   @param numOmit integer of how many keywords to omit
"""
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
   Extracts and returns 2d list of lidar scans from file
   @param fileName of file to extract
   @param keyword of where scan begins
   @param numOmit how many keywords to omit at start of file
   @param numAfter how many points after keyword to skip over
   @param numPoints how many lidar distance points there are
   @param numPointsCollect how many lidar distance points to collect
"""
def scrapeLidarScans(fileName, laserkeyword, odomkeyword, numOmit, numAfter):
    scanSet = []
    numPoints = 360
    #Compensate for the keyword itself
    numAfter = numAfter+1
    rightBound = numPoints + numAfter
    #Open file and turn into string
    with open(fileName, 'r') as file:
        strFile = file.read()
    j = -1
    count = 1
    #Skip over omitted instances of keyword
    for i in range(numOmit+1):
        j = strFile.find(laserkeyword, j+1)
    #Loop while there are more keywords
    while (j != -1):
        #Cut out string lidar measurements
        strValues = strFile[j:].split(' ', rightBound)[numAfter:rightBound]

        #Convert data to float
        final = floatify(strValues, True)
        scanSet.append(final)
        j = strFile.find(laserkeyword, strFile.find(odomkeyword, j+1))
        count = count + 1
    return scanSet


"""
   extracts and returns Odom element lists
   @param filename of dataset
   @param keyword - generally 'ODOM'
   @param numOmit number of omissions of keyword at start of the dataset
   @param numPoints number of values to grab at each datapoint
"""
def scrapeOdom(fileName, odomkeyword, laserkeyword, numOmit, numAfter):
    odomSet = []
    numPoints = 2
    #Compensate for keyword itself
    numAfter = numAfter + 1
    rightBound = numAfter + numPoints
    #Open file and turn into string
    with open(fileName, 'r') as file:
        strFile = file.read()
    j = -1
    count = 1
    #Skip over first occurances of keyword
    for i in range(numOmit+1):
        j = strFile.find(odomkeyword, j+1)
    #Loop while there are more keywords
    while (j != -1):
        #Cut keyword and preceeding data
        strValues = strFile[j:].split(' ', rightBound)[numAfter:rightBound]

        final = floatify(strValues, False)
        odomSet.append(final)
        j = strFile.find(odomkeyword, strFile.find(laserkeyword, j+1))
        count = count + 1

    return odomSet
         

"""
   Extracts all necessary information using the functions above
"""
def scrapeFile(fileName, lidarKeyword, lidarOmit, lidarNumAfter, odomKeyword, odomOmit, xYNumAfter, tvRvNumAfter, verbose):
    #Extract data into lists
    scans = scrapeLidarScans(fileName, lidarKeyword, odomKeyword, lidarOmit, lidarNumAfter)
    if (verbose): print('Lidar Scans scraped. | Scraping x & y positions...')
    xY = scrapeOdom(fileName, odomKeyword, lidarKeyword, odomOmit, xYNumAfter)
    if (verbose): print('x & y positions scraped. | Scraping velocities...')
    tvRv = scrapeOdom(fileName, odomKeyword, lidarKeyword, odomOmit, tvRvNumAfter)
    if (verbose):print('velocities scraped.')

    numPoints = countKeywords(fileName, lidarKeyword, lidarOmit)

    return scans, tvRv, xY, numPoints


