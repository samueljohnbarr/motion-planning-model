import scraper
import extractMemory
import dataFormat

datasetDir = './rawData/'
""" 
    ############## Dataset Parameter Format ###############
    <file name>,
    <lidar keyword>,
    <# of lidar keywords to omit>,
    <# of values to skip after lidar keyword>,
    <odometer keyword>,
    <# of odometer keywords to omit>,
    <# of values to skip after odom keyword for x/y position>
    <# of values to skip after odom keyword for velocities (tv/rv)>
    <scrape: 'True' will scrape the dataset and save extracted data>
"""

datasets = [ 
('mit-csail-3rd-floor-2005-12-17-run4.log', 'ROBOTLASER1', 2, 8, 'ODOM', 2, 0, 3, True),
('fr-campus-20040714.carmen.log', 'FLASER', 6, 2, 'ODOM', 5, 0, 3, True),
('fr101.carmen.log', 'FLASER', 2, 1, 'ODOM', 2, 0, 3, True),
('belgioioso.log', 'FLASER', 4, 1, 'ODOM', 6, 0, 3, True),
('fr079-complete.log', 'FLASER', 2, 1, 'ODOM', 5, 0, 3, True),
('seattle-r.gfs.log', 'FLASER', 0, 1, 'ODOM', 71, 0, 3, False) 
]
          
"""
   Scrapes data from datasets lists if the dataset is marked
   for scraping.
   Saves scraped data into its own directory.
"""
def scrapeData(verbose):
    for dset in datasets:
        #Check if dataset is marked for scraping
        if dset[-1]:
            if (verbose): 
                print('Scraping', dset[0])
                print('This may take a while...')

            #Grab components of tuple
            fname, lkeywrd, lomit, lnAfter, okeywrd, oomit, xynAfter, \
                    vnAfter = dset[:-1]
            #Scrape data
            path = datasetDir + fname
            scans, tvRv, xY, numPoints = scraper.scrapeFile(path, lkeywrd, lomit, lnAfter, \
                        okeywrd, oomit, xynAfter, vnAfter, verbose)
            if (verbose): print('Data components extracted')

            #Calculate target vector
            targets = dataFormat.calcTargetData(xY)
            if (verbose): print('Target calculation completed')

            #Save Extracted Data
            setName = fname[:6]
            extractMemory.saveExtractedSet(setName, scans, targets, tvRv, numPoints)
            if (verbose): 
                print('Extracted data saved in extractedData/'+setName)
                print('Done.')

"""
   Reads extracted data and formats it for input to the model
   @return train/test sets of lidar data, target data, 
   velocity (labeled) data and number of samples
"""
def getData():
    #Grab data from extracted files
    lidar, targets, tvRv, numSamples = extractMemory.readExtractedData()
    
    #Format data
    lTrain, lTest, tTrain, tTest, vTrain, vTest = dataFormat.format( \
            lidar, targets, tvRv)

    return lTrain, lTest, tTrain, tTest, vTrain, vTest, numSamples


