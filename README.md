# motion-planning-model
This is my graduate project for Appalachian State University and is an implementation of Phieffer et al's *From Perception to Decision: A Data Driven Approach to Autonomous Ground Robots*.
The goal of my implementation is to train a model to drive a robot through indoor evironments given that the robot is equiped with a LiDAR.

## model.py 
### Usage
Since I am currently in the training phase of development, functionality is limited to just that.
```
model.py <verbosity> <function>
    <verbosity>: -v
    <function>: train | reset
Examples:
    model.py -v train
    model.py reset
```

### Description
The idea of the model is to think like a human would - Given what you can see of your surroundings and an idea of where you want to go, drive in that direction without hitting anything.  This is done using *keras*, an machine learning API built on Google's *Tensorflow* framework. The implemented model is a residual convolutional neural network (CNN) where the input is a length 360 distance vector (LiDAR output).  The distance vector is sent through the CNN and its output is then fused with target information.  The fused data is then sent through the fully connected layers and the final output is translational and rotational velocities meant to drive the robot. 

Upon training, the loss (the difference between the model output velocities and the actual velocities) is calculated using mean-squared-error.  The optimization function (how the model uses loss to alter its learned weights) is the Adam optimizer.

## extract.py
*I am currently refactoring this script and therefore it is not functional at the moment. 'extract-old.py' works, but is terribly messy and nearly unreadable.*

### Usage
Using this is a bit more involved than model.py. Within the file, a dataset tuple contains everything the script needs to know for extracting data components from a dataset. Parameters are defined in detail within the file, but they must be hardcoded in a tuple for scraping to work properly. A boolean value at the end of the tuple determines if the script should scrape that dataset or not.

### Description
Every machine learning model needs data to train with.  This is the driver script to scrape data from multiple datasets and prepare it for the model to train with. Helper scripts are scraper.py, dataFormat.py, and io.py.  Scraping data and preparing it for the model is done in two separate processes.  It first scrapes lidar data, x/y positioning, and translational/rotational velocities from a dataset.  It then uses x/y postioning to calculate polar target positions using vector addition. Once completed, it saves those components into respective files in the 'extractedData' folder.
Since scraping data from large datasets takes a considerable amount of time, this process of saving scraped data and reading it when needed is much more efficient.  When model input data is needed, the script will read in all extracted data, format it, and split it into training and testing sets.
