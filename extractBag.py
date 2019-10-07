import rosbag

scans = []


def readFile(fileName):
    with rosbag.Bag(fileName, 'r') as bag:
        for msg_topic, msg, t in bag.read_messages(topics=['/scan', '/odom']):
            scans.append(msg)


readFile('2D-laser-datasets/floor1.bag')
print(scans[99])
