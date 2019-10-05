import scraper.py
import data-io.py
import format-data.py

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
('mit-csail-3rd-floor-2005-12-17-run4.log', 'ROBOTLASER1', 2, 1, 'ODOM', 2, 1, 4, True),
('fr-campus-20040714.carmen.log', 'FLASER', 6, 1, 'ODOM', 5, 1, 4, False),

('fr101.carmen.log', 'FLASER', 2, 1, 'ODOM', 2, 1, 4, False),
('belgioioso.log', 'FLASER', 4, 1, 'ODOM', 4, 1, 4, False),
('fr079-complete.log', 'FLASER', 2, 1, 'ODOM', 2, 1, 4, False),
('seattle-r.gfs.log', 'FLASER', 0, 1, 'ODOM', 2, 1, 4, False)
]
#TODO the last two have dummy values for ODOM info
          
"""
   
"""
def scrapeData():
    for dset in datasets:
        #Check if dataset is marked for scraping
        if dset[-1]:
            fname, lkeywrd, lomit, lnAfter, okeywrd, oomit, xynAfter, vnAfter = dset[:-1]


scrapeData()
print(':)')

            

