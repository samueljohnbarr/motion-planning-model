# from_tensor_slices returns:
# TypeError: Expected binary or unicode string, got [ ... (Lidar floats) ... ]

import tensorflow as tf
import numpy as np
import math
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
from tensorflow.keras.models import Model
from tensorflow.keras.layers import concatenate
from tensorflow.keras.layers import Lambda
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Reshape
from sklearn.model_selection import train_test_split

#Graphing
#import matplotlib.pyplot as plt

#Logging 
import logging
logger = tf.get_logger()
logger.setLevel(logging.ERROR)

#*****************SETUP*****************#
#*BATCH SIZE
batch_size = 32

#Grab the dataset
dataset = extract.readExtractedData()
print('Data Extracted\n')
training_lidar = dataset[0]
training_targets = dataset[1]
training_labels = dataset[2]
numSamples = extract.getNumSamples()


#Partition data into training and testing sets
lidarTrain, lidarTest, targetTrain, targetTest = train_test_split(
       training_lidar, training_targets, test_size=0.25, random_state=42)


#Expand dimensionality of input data
a = 1
lidarTrain = np.expand_dims(lidarTrain, axis=a)
lidarTest = np.expand_dims(lidarTest, axis=a)
targetTrain = np.expand_dims(targetTrain, axis=a)
targetTest = np.expand_dims(targetTest, axis=a)

print('Lidar Shape: ', lidarTrain.shape)
print('Target Shape: ', targetTrain.shape)

#Split and format labeled data
split = int(math.floor(numSamples*0.75)) - 1
print('numSamples:', numSamples)
print('split:', split)
trainLabels = training_labels[:split]
testLabels = training_labels[split:]

trainLabels = np.expand_dims(trainLabels, axis=a)
testLabels = np.expand_dims(testLabels, axis=a)


#Print data lengths (testing) 
print('lidarTrain', len(lidarTrain))
print('lidarTest', len(lidarTest))
print('targetTrain', len(targetTrain))
print('targetTest', len(targetTest))
print('trainLabels', len(trainLabels))
print('testLabels', len(testLabels))

print('Data pulled, batched, and preprocessed')


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



def createModel():
    filter_size = 64

    #Create First Block
    X_input = Input(shape=(1,359))
    #X = Flatten()(X_input)
    X = Conv1D(filter_size, (7), 3, padding='same', activation=tf.nn.relu,
            input_shape=(lidarTrain.shape))(X_input)
    X = BatchNormalization()(X)
    X = MaxPooling1D((3), 1, padding='same')(X)

    #**************CNN RESIDUAL*****************
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
    
    #Add last pooling layer
    X = AveragePooling1D((3), 1, padding='same')(X)
    #X = Flatten()(X)
    X = Model(inputs=X_input, outputs=X)
    #*************END CNN************    

    #Add a secondary input to hidden layer for target info
    Y_in = Input(shape=(1,2))
    #Y = Flatten()(Y_in)
    Y = Lambda(lambda x: x)(Y_in)
    Y = Model(inputs=Y_in, outputs=Y) 
    
    #Combine new input with output of CNN
    combined = concatenate([X.output, Y.output], axis=2) #prev: 1

    #Add Fully Connected Layers
    Y = Dense(256, activation=tf.nn.relu)(combined)
    Y = Dense(256, activation=tf.nn.relu)(Y)
    Y = Dense(256)(Y)
    Y = Dense(2)(Y)

    model = Model(inputs=[X_input, Y_in], outputs=Y)

    return model


model = createModel()
print('Compiling Model...')
#Compile Model
model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.1))

print('Initiating Training...')
#Train Model
history = model.fit([lidarTrain, targetTrain], trainLabels, 
        validation_data=([lidarTest, targetTest], testLabels), epochs=5, batch_size=numSamples)

print('Training Completed.')
#Batch data affects epochs here


#Evaluate Accuracy
