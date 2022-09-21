#!/usr/bin/env python

import rospy
import sys
import rospkg
import numpy as np
import pandas as pd
import math as m
import genpy
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point, Quaternion, Vector3, PoseStamped, PoseArray
from std_msgs.msg import ColorRGBA
from mission.msg import obTF


"""
Subscribe 'scan_filtered' and
Publish 'ob_TF'
"""


class Lidar(object):
    def __init__(self, state):
        super(Lidar, self).__init__()

        path_data = pd.read_csv("/home/acca/catkin_ws/src/ACCA2022-new/mission/data/sc/dynamic_path.csv")
        self.path_cx = path_data.cx.tolist()
        self.path_cy = path_data.cy.tolist()
        self.path_cyaw = path_data.cyaw.tolist()
        self.path = []
        for i in range(len(self.path_cx)):
            self.path.append([self.path_cx[i], self.path_cy[i]])
            
        self.state = state
        
        self.thr_dis = 3.
        self.thr_path_dis = 1.0
        
        rospy.Subscriber("/scan_filtered", LaserScan, self.laserCallback)
        self.obs_pub_parking = rospy.Publisher("parking_position", MarkerArray, queue_size=10)        
        self.part_pub = rospy.Publisher("ob_TF", obTF, queue_size=5)


    def laserCallback(self, msg):
        self.ranges = msg.ranges


    def GetDistance(self, path, point):           
        dis_r_array = []  
        for i in range(len(path)):
            dis = m.sqrt((point[0] - path[i][0]) ** 2 + (point[1] - path[i][1]) ** 2)
            dis_r_array.append(dis)     
        min_dis = min(dis_r_array)
        return min_dis
    
    
    def publishPoint(self, point):
        msg = MarkerArray()
        for i in range(len(point)):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = rospy.Time.now()
            marker.ns = str(i)
            marker.id = 1
            marker.type = 3
            marker.action = 0
            marker.pose.position = Point(point[i][0], point[i][1], 0.)
            marker.pose.orientation = Quaternion(0., 0., 0., 1)
            marker.scale = Vector3(0.1, 0.1, 0.1)
            marker.color = ColorRGBA(1., i/40, 0., 1.)
            marker.lifetime = genpy.Duration(secs=0.2)
            msg.markers.append(marker)
        self.obs_pub_parking.publish(msg)
        
        
    def detect_range(self):
        self.mapping = []
        self.obstacle = []
        
        for i in range(1, 41):
            
            theta = (-10 + (i / 2)) * np.pi * 180
            lidar_x = self.ranges[158+i] * m.cos(theta)
            lidar_y = self.ranges[158+i] * m.sin(theta)
            map_x = self.state.x + lidar_x * m.cos(self.state.yaw) - lidar_y * m.sin(self.state.yaw)
            map_y = self.state.y + lidar_x * m.sin(self.state.yaw) + lidar_y * m.cos(self.state.yaw)
            
            dis_path = self.GetDistance(self.path, [map_x, map_y])
            
            self.obstacle.append([self.ranges[158+i], dis_path])
            self.mapping.append([map_x, map_y])
            
            
    def Result(self):
        
        obs_num = 0
        partTF = obTF()

        for i in self.obstacle:
            
            if i[0] < self.thr_dis and i[1] < self.thr_path_dis:
                obs_num += 1
            
        if obs_num >= 5:
            partTF.front_right = 1
            partTF.front_left = 1
            partTF.side_right = 0
            partTF.side_left = 0
            
        else:
            partTF.front_right = 0
            partTF.front_left = 0
            partTF.side_right = 0
            partTF.side_left = 0

    def main(self):
        self.detect_range()
        self.Result()
        self.publishPoint(self.mapping)