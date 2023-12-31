#!/usr/bin/env python

import rospy
import rospkg
import numpy as np
import math as m
import csv
from enum import Enum
from path_plan.msg import PathRequest, PathResponse


class Waypoint(object):
    def __init__(self, id, is_end):
        self.id = id
        self.is_end = is_end


def findWaypoint(file_path, id):
    with open(file_path, "r") as csvFile:
        reader = csv.reader(csvFile, delimiter=",")
        for row in reader:
            if id == row[0]:
                return Waypoint(id=row[0], is_end=("1" == row[3]))


class Node(object):
    def __init__(self, data, start, end, next=None):
        self.data = data
        self.next = next

        self.start = start
        self.end = end
        self.type = None

    def append(self, data):
        self.next = data


class PathSelector(object):
    def __init__(self, state):
        self.state = state

        self.req_pub = rospy.Publisher(
            "/path_request", PathRequest, queue_size=1)

        # Get All Path Data
        self.path = None
        self.getAllPath()

    def goNext(self):
        if self.path.next is not None:
            self.path = self.path.next
            return self.path

        return None

    def makeRequest(self):
        if self.path is None:
            rospy.logwarn("Loading Path Data...")
            return 0

        # rospy.loginfo("Send Request...")
        # rospy.loginfo(self.path.data)

        self.req_pub.publish(self.path.data)

    def getAllPath(self):
        waypoints_path = rospkg.RosPack().get_path("path_plan") + "/waypoints/" + \
            rospy.get_param("/waypoints/waypoints_file", "waypoints.csv")
        file_path = rospkg.RosPack().get_path("path_plan") + "/path/" + \
            rospy.get_param("/LoadPath/path_name", "path.csv")

        node = None

        with open(file_path, "r") as csvFile:
            reader = csv.reader(csvFile, delimiter=",")
            for row in reader:
                try:
                    start = row[0]
                    end = row[1]

                    print(start, end)

                    start_point = findWaypoint(waypoints_path, id=start)
                    end_point = findWaypoint(waypoints_path, id=end)

                    temp = Node(PathRequest(start, end, start+end),
                                start=start_point, end=end_point)

                    if node is None:
                        node = temp
                        self.path = node

                    else:
                        node.append(temp)
                        node = temp

                except Exception as ex:
                    rospy.logwarn(ex)

        return 0
