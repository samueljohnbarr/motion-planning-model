import sys
import os
import serial
from datetime import datetime
import numpy as np
from sklearn.preprocessing import normalize
import model as mod

#Port info
port = '/dev/bus/usb/002/006'
###############################
# sudo chmod 666 /dev/ttyUSB0 #
###############################

#Collect Mode
COLLECT = True

#Control bytes
REQUEST = b'\xa5'  #Request to speak
ACK     = b'\x5a'  #Acknowlege recieved transmission
STOP    = b'\xb5'  #Notify reviever that transmission is ending
END     = b'\x5b'  #End of current transmission

#Date info
today = datetime.today()

def flush_buffer():
    count = 0
    while ser.in_waiting:
        ser.read(1)
        count += 1
    print('flushed', count, 'bytes')


def wirelessSend(payload):
    #Initiate connection
    ser.write(REQUEST)
    print('Waiting for ACK...')
    ans = ser.read(1)

    #Send payload
    if (ans == bytes(ACK)):
        print('Sending Payload')
        for i in range(2):
            print(bytes(str(payload[0][0][i]).encode('utf-8')))
            ser.write(bytes(str(payload[0][0][i]).encode('utf-8')))
            ser.write(END)

        print('Payload sent')
        ser.write(STOP)
        ans = ser.read(1)

        #Warning if sent payload not acknowledged
        if (ans != bytes(ACK)):
            print('Reciever did not acknowledge transmission')
    else:
        ser.write(STOP)
        print('Recieved non-ACK byte for connection request')


def wirelessRecieve():
    buf = []
    print('Port listening for transmission...')
    #Wait for robot to speak first
    while not ser.in_waiting:
        pass
    print('port has data to read')
    #Receive request byte
    req = ser.read(1)
    if (req == bytes(REQUEST)):
        #Acknowledge Request
        ser.write(ACK)
        size = int(ser.readline())
        print('Payload size:', size)
        for i in range(size*2):
            data = ser.readline()
            val = data.decode('utf-8').split('\n')
            buf.append(val[0])
    else:
        ser.write(STOP)
        print("Recieved non-start byte at beginning of transmission:", req)
    
    print('Receiving STOP')
    stp = ser.read(1)
    if (stp == STOP):
        ser.write(ACK)

    #Format data
    buf = buf[0::2]
    for i in range(len(buf)):
        buf[i] = int(buf[i])
    print('data read complete')

    return buf


def formatModelInput(lidar, target):
    l = np.array(lidar)
    t = np.array(target)

    npLidar = normalize(l.reshape(l.shape[0], -1), norm='l2', axis=0).reshape(l.shape)
    npTarget = normalize(t.reshape(t.shape[0], -1), norm='l2', axis=0).reshape(t.shape)

    npLidar = np.expand_dims(np.expand_dims(npLidar, axis=0), axis=1)
    npTarget = np.expand_dims(np.expand_dims(npTarget, axis=0), axis=1)

    return npLidar, npTarget


def retrieveModelInput():
    lidarScan = []
    target = []
    for i in range(2):
        flush_buffer()
        #Get data
        data = wirelessRecieve()
        #Organize it
        if (len(data) == 360):
            lidarScan = data
        elif (len(data) == 2):
            target = data
    print(lidarScan)
    print(target)
    if (COLLECT):
        saveCollectedData(l=lidarScan, t=target)
    lidarScan, target = formatModelInput(lidarScan, target)

    return lidarScan, target
   

def saveSet(filePath, setToSave):
    f = open(filePath, "a+")
    for i in setToSave:
        f.write("%f\n" % i)
    f.write("\n")
    f.close()


def saveCollectedData(l=[], t=[], v=[]):
    date = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
    time = str(today.hour) + ':' + str(today.minute)
    
    #Overall collected data folder
    filePath = './collectedData/'
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    
    #Subdirectory cooresponding to date
    filePath = filePath + date + '/'
    if not os.path.exists(filePath):
        os.mkdir(filePath)

    #Subdirectory cooresponding to time
    filePath = filePath + time + '/'
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    
    if (len(l) > 0):
        saveSet(filePath + 'lidar.txt', l)
    if (len(t) > 0):
        saveSet(filePath + 'targets.txt', t)
    if (len(v) > 0):
        saveSet(filePath + 'velocties.txt', v)



"""
   Feedback loop from this machine to the robot.
   Robot will first send its lidar data and target.
   Lidar and target info is sent through the model
   and then sent back to the robot.
   (((If collection is True, all data sent and recieved 
      s saved in 'collectedData' directory)))
   Rinse and repeat.
"""
def modelFeedback():
    model = mod.initModel()
    velocities = []
    while(True):
        lidar, target = retrieveModelInput()
        prediction = model.predict([lidar, target])
        print('Prediction:', prediction)

        #Save collected data
        if (COLLECT):
            velocities.append(prediction[0][0][0])
            velocities.append(prediction[0][0][1])
            saveCollectedData(v=velocities)
        #Send back prediction (velocities)   
        wirelessSend(prediction)


"""
   Just saves data recieved into timestamped files.
   Does not send any information back to the
   robot.
"""
def dataCollection():
    while (True):
        pass


modelFeedback()
ser.close()
