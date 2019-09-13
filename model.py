# from_tensor_slices returns:
# TypeError: Expected binary or unicode string, got [ ... (Lidar floats) ... ]

import tensorflow as tf
import numpy as np
import extract

from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import MaxPooling1D
from tensorflow.keras.layers import AveragePooling1D
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import InputLayer
from tensorflow.keras.layers import Add

#Graphing
#import matplotlib.pyplot as plt

#Logging 
import logging
logger = tf.get_logger()
logger.setLevel(logging.ERROR)

#Grab the dataset
dataset = extract.readExtractedData()
print('Data Extracted\n')
training_data = dataset[0]
training_labels = dataset[1]

#Partition the dataset into train and test sets - TODO fix partition sizes
indices = np.random.permutation(training_data.shape[0])
train_idx, test_idx = indices[:80], indices[80:]
training, test, train_labels, test_labels = training_data[train_idx,:], training_data[test_idx,:], training_labels[train_idx,:], training_labels[test_idx,:]
print('Data Partitioned\n')

#Convert to tf friendly input - TODO fix all this shit yo
train_dataset = tf.data.Dataset.from_tensor_slices((training, train_labels))
test_dataset = tf.data.Dataset.from_tensor_slices((test, test_labels))

#Batch the data here
batch_size = 32
numSamples = extract.getNumSamples() 

train_dataset = train_dataset.repeat().shuffle(numSamples).batch(batch_size)
test_dataset = test_dataset.batch(batch_size)

print('Data shuffled, batched, and preprocessed')


def createResBlocks(X, filter_size):
    """ Creates the residual part of the model (like 80% of the entire model)
        Including all skip connections
        X - input tensor
        filter_size - size of kernel for convolutions
    """
    #Save input Tensor
    X_shortcut = X

    #First Component of main path
    X = Conv1D(filter_size, (3), 1, padding='same')(X)
    X = BatchNormalization()(X)
    X = Activation('relu')(X)

    #Second Component of main path
    X = Conv1D(filter_size, (3), 1, padding='same')(X)
    X = BatchNormalization()(X)

    #Save second shortcut
    X_shortcut1 = X

    #Add first shortcut value to main path and pass it through ReLU
    X = Add()([X, X_shortcut])
    X = Activation('relu')(X)

    #Third Component of main path
    X = Conv1D(filter_size, (3), 1, padding='same')(X)
    X = BatchNormalization()(X)
    X = Activation('relu')(X)

    #Fourth Component of main path
    X = Conv1D(filter_size, (3), 1, padding='same')(X)
    X = BatchNormalization()(X)

    #Add second shortcut value to main path and pass it through ReLU
    X = Add()([X, X_shortcut1])
    X = Activation('relu')(X)

    return X

def createFCLayers(X, n):
    """ Creates the fully connected layers of the model
        X - input tensor
        n - number of neurons per layer
    """
    for i in range(3): 
        X = Dense(n, activation=tf.nn.relu)(X)
    
    return X


def createModel():
    #Create First Block
    X_input = Input(shape=(None,360))
    
    X = Conv1D(64, (7), 3, padding='same', activation=tf.nn.relu)(X_input)
    X = BatchNormalization()(X)
    X = MaxPooling1D((3), 1)(X)
    
    #Add Residual Blocks
    X = createResBlocks(X, 64)

    #Add last pooling layer
    X = AveragePooling1D((3), 1)(X)

    #Add a secondary input to hidden layer for target info
    X = InputLayer(input_shape=(None,1))(X)
    
    #Add Fully Connected Layers
    X = createFCLayers(X, 256)
    
    return X


model = createModel()
print('Compiling Model...')
#Compile Model
model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.1))

print('Initiating Training...')
#Train Model
history = model.fit(train_dataset, epochs=5, steps=math.ceil(len(test_data)/batch_size))

print('Training Completed.')
#Batch data affects epochs here


#Evaluate Accuracy
