import tensorflow as tf
import tensorflow.keras.backend as K
import numpy as np
import math
import sys
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
from tensorflow.keras.initializers import glorot_uniform
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize

#Logging 
import logging
logger = tf.get_logger()
logger.setLevel(logging.ERROR)

VERBOSE = False
TRAIN = False

#BATCH SIZE TODO
batch_size = 32


def getData():
    """
       Grabs extracted data and prepares it for input to the model
    """
    #Grab the dataset
    training_lidar, training_targets, training_labels = extract.readExtractedData()
    numSamples = extract.getNumSamples()
    if VERBOSE: print('Number of training samples:', numSamples)

    #Normalize input data
    training_lidar = normalize(training_lidar, norm='l2')
    training_targets = normalize(training_targets, norm='l2')

    #Partition data into training and testing sets
    lidarTrain, lidarTest, targetTrain, targetTest, labelTrain, labelTest = train_test_split(training_lidar, training_targets, training_labels, test_size=0.25, random_state=42)

    #Expand dimensionality of input data
    a = 1
    lidarTrain = np.expand_dims(lidarTrain, axis=a)
    lidarTest = np.expand_dims(lidarTest, axis=a)
    targetTrain = np.expand_dims(targetTrain, axis=a)
    targetTest = np.expand_dims(targetTest, axis=a)
    labelTrain = np.expand_dims(labelTrain, axis=a)
    labelTest = np.expand_dims(labelTest, axis=a)

    if VERBOSE: print('Training input shape:', lidarTrain.shape)
    if VERBOSE: print('Testing input shape:', lidarTest.shape)

    return lidarTrain, lidarTest, targetTrain, targetTest, labelTrain, labelTest



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
    #**** Convolutional Network ****#
    #Create First Block
    X_input = Input(shape=(1,360))
    X = Conv1D(filter_size, (7), 3, padding='same', activation=tf.nn.relu)(X_input)
    X = BatchNormalization()(X)
    X = MaxPooling1D((3), 1, padding='same')(X)
    
    #Create Residual Blocks
    X = createResBlocks(X, filter_size)
    
    #Add last pooling layer of CNN
    X = AveragePooling1D((3), 1, padding='same')(X)
    X = Model(inputs=X_input, outputs=X)

    #**** Fully Connected Layers ****#    
    #Add a secondary input to hidden layer for target info
    Y_in = Input(shape=(1,2))
    Y = Lambda(lambda x: x)(Y_in)
    Y = Model(inputs=Y_in, outputs=Y) 
    
    #Combine new input with output of CNN
    combined = concatenate([X.output, Y.output], axis=2)

    #Add Fully Connected Layers
    Y = Dense(256, activation=tf.nn.relu)(combined)
    Y = Dense(256, activation=tf.nn.relu)(Y)
    Y = Dense(256)(Y)
    Y = Dense(2)(Y)

    model = Model(inputs=[X_input, Y_in], outputs=Y)

    return model


def resetModel():
    """ Randomly sets weights for the entire model
        Exits program when completed
    """
    model = createModel()
    model.compile(loss='mean_squared_error',optimizer=tf.keras.optimizers.Adam(0.1))
    initial_weights = model.get_weights()
    k_eval = lambda placeholder: placeholder.eval(session=K.get_session())
    new_weights = [k_eval(glorot_uniform()(w.shape)) for w in initial_weights]
    model.set_weights(new_weights)
    print('All weights have been reset to random values.')
    exit(0)



#++++++++++++++++++++++++++++++++EXECUTION POINT++++++++++++++++++++++++++++++++++++#
print()
#Process cmd line args
if len(sys.argv) > 1:
    for i in sys.argv:
        if (i == '-v'):
            VERBOSE = True
        elif (i == 'reset'):
            resetModel()
        elif (i == 'train'):
            TRAIN = True            
else:
    print('USAGE: python3 model.py <verbosity> <function>')
    print('Verbose mode: -v')
    print('Functions: \'train\' | \'reset\'')
    exit(0)


if VERBOSE: print('Preparing Model & Data...')
model = createModel()

if VERBOSE: print('Compiling Model...')
model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.1))

if VERBOSE: print('Preparing Input Data...')
lidarTrain, lidarTest, targetTrain, targetTest, labelTrain, labelTest, numSamples = extract.getData()


if (TRAIN):
    if VERBOSE: print('Initiating Training...')
    history = model.fit([lidarTrain, targetTrain], labelTrain, 
        validation_data=([lidarTest, targetTest], labelTest), epochs=5, batch_size=numSamples)
    if VERBOSE: print('Training Completed.')

#Evaluate Accuracy

