import numpy as np
import pptk

def import_file(filePath):
    #Read in and split data into string list
    f = open(filePath, 'r')
    data = f.read()
    f.close()
    listData = data.splitlines()
    #Convert to float list
    floatData = []
    for i in range(len(listData)-1):
        floatData.append(float(listData[i]))

    return floatData


def calc_xy(data):
    x,y,z = [],[],[]
    c = 0

    for i in data:
        if (c < 90):
            x.append((i * np.sin(c * np.pi/180)))
            y.append((i * np.cos(c * np.pi/180)))
        if (c >= 90 and c < 180):
            x.append((i * np.cos((c-90) * np.pi/180)))
            y.append((-i * np.sin((c-90) * np.pi/180)))
        if (c >= 180 and c < 270):
            x.append((-i * np.sin((c-180) * np.pi/180)))
            y.append((-i * np.cos((c-180) * np.pi/180)))
        if (c >= 270 and c < 360):
            x.append((-i * np.cos((c-270) * np.pi/180)))
            y.append((i * np.sin((c-270) * np.pi/180)))
        z.append(0)
        c += 1

    return np.vstack((x,y,z)).T.astype(int)


data = import_file('extractedData/carmenLidarScans.txt')
xy_data = calc_xy(data)
v = pptk.viewer(xy_data)
v.set(point_size=0.8)
v.attributes(xy_data)


