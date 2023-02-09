#!/usr/bin/env python3

from getmac import get_mac_address
from rpi_project.msg import DistanceMsg
import math
import subprocess
import statistics
import numpy as np
import rospy
import time

Rpi0_dist = []
Rpi2_dist = []
Rpi3_dist = []

Rpi0_published_dist = []
Rpi2_published_dist = []
Rpi3_published_dist = []

def get_RSSI(line):

    first_index = line.find("rssi")
    last_index = line.find("flags")

    rssi = int(line[first_index+5:last_index-1])

    return rssi

def get_my_Mac_Address():

    return get_mac_address(interface="eth0")

def get_Scans():

    p = subprocess.Popen("sudo btmgmt find |grep rssi |sort -n |uniq -w 33", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return p.stdout.readlines()

def get_Rpies(scans, mac_addresses):

    rpies = {}

    for line in scans:
        line = str(line)
        for mac_address in mac_addresses:
            if(mac_address in line):
                rssi = get_RSSI(line)
                rpies[mac_address] = rssi
            else:
                continue

    return rpies

def get_Distance(rpies):
    '''
        Distance = 10 ^ ((Measured Power - RSSI) / (10 * N))

        Measured Power = izmjereni rssi
        RSSI = offset vrijednost; rssi na udaljenosti od 1 m (-70 dB)
        N = konstanta vrijednosti 2

    '''

    distance = {}
    N = 2
    rssi = -70

    for key in rpies.keys():
        dist = math.pow(10, (rpies.get(key) - rssi) / (10 * N))
        distance[key] = dist

    return distance

def get_Median_Distance(distance):

    if (len(Rpi0_dist) < 5):
        for key in distance.keys():
            if (key == "DC:A6:32:FB:26:63"):    # Rpi0
                Rpi0_dist.append(distance.get(key))
    elif(len(Rpi0_dist) == 5):
        for key in distance.keys():
            if (key == "DC:A6:32:FB:26:63"):
                Rpi0_dist.append(Rpi0_dist.pop(0))
                Rpi0_dist.remove(Rpi0_dist[4])
                Rpi0_dist.append(distance.get(key))

    if (len(Rpi2_dist) < 5):
        for key in distance.keys():
            if (key == "DC:A6:32:D4:3F:56"):    # Rpi2
                Rpi2_dist.append(distance.get(key))
    elif(len(Rpi2_dist) == 5):
        for key in distance.keys():
            if (key == "DC:A6:32:D4:3F:56"):
                Rpi2_dist.append(Rpi2_dist.pop(0))
                Rpi2_dist.remove(Rpi2_dist[4])
                Rpi2_dist.append(distance.get(key))

    if (len(Rpi3_dist) < 5):
        for key in distance.keys():
            if (key == "DC:A6:32:D4:3F:A6"):    # Rpi3
                Rpi3_dist.append(distance.get(key))
    elif(len(Rpi3_dist) == 5):
        for key in distance.keys():
            if (key == "DC:A6:32:D4:3F:A6"):
                Rpi3_dist.append(Rpi3_dist.pop(0))
                Rpi3_dist.remove(Rpi3_dist[4])
                Rpi3_dist.append(distance.get(key))

    median_dis = []
    if (Rpi0_dist):
        median_dis.append(statistics.median(Rpi0_dist))
    else:
        median_dis.append(0)
    median_dis.append(0)
    if (Rpi2_dist):
        median_dis.append(statistics.median(Rpi2_dist))
    else:
        median_dis.append(0)
    if (Rpi3_dist):
        median_dis.append(statistics.median(Rpi3_dist))
    else:
        median_dis.append(0)

    return median_dis

def publish_Distances(median_dis):

    pub = rospy.Publisher('rpi1_topic', DistanceMsg, queue_size=10)
    rate = rospy.Rate(1) # 10 Hz

    i = 0
    while not rospy.is_shutdown():

        rospy.loginfo(median_dis)
        pub.publish(median_dis)
        rate.sleep()

        i = i+1
        if i > 5:
            break

def callback(data):

    rospy.loginfo(" I heard {}".format(data))
    Rpi3_published_dist = list(data.list) 

def get_Other_Distances(topic):

    #print("Cekam distance...")
    #dis = rospy.wait_for_message(topic, DistanceMsg)
    rospy.Subscriber(topic, DistanceMsg, callback)
    time.sleep(10)
    #rospy.spin()

def get_Matrix(median_dis):
    dist_matrix = np.zeros((4,4))

    #dist_matrix[0] = Rpi0_published_dist
    dist_matrix[1] = median_dis
    #dist_matrix[2] = Rpi2_published_dist
    #dist_matrix[3] = Rpi3_published_dist

    return dist_matrix

if __name__ == "__main__":

    mac_addresses = ["DC:A6:32:FB:26:63","DC:A6:32:D4:3F:56","DC:A6:32:D4:3F:A6"]

    rospy.init_node('Rpi1', anonymous=True)

    for i in range(10):
        print("\nKorak %d.\n" % (i+1))
        scans = get_Scans()

        rpies = get_Rpies(scans, mac_addresses)

        distance = get_Distance(rpies)

        median_dis = get_Median_Distance(distance)

        #publish_Distances(median_dis)
        #get_Other_Distances("rpi3_topic")
        #print(Rpi3_published_dist)

        dist_matrix = get_Matrix(median_dis)

        print("Rpi0: {}".format(Rpi0_dist))
        print("Rpi2: {}".format(Rpi2_dist))
        print("Rpi3: {}".format(Rpi3_dist))
        print("\n")
        print(dist_matrix)
