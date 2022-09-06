#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import math as m
import rospy
from visualization_msgs.msg import *
from geometry_msgs.msg import *
from std_msgs.msg import Int16, Int32
from parking_area import ParkingArea
from std_msgs.msg import ColorRGBA
from genpy import Duration
import numpy as np
from copy import deepcopy
from tf.transformations import euler_from_quaternion
from nav_msgs.msg import Odometry

the_number_of_parkinarea = 6
All_of_parking_area = [1, 2, 3, 4, 5, 6]


def checkIsInParking(obstacle, center_point_of_area):
    dist = np.hypot(
        center_point_of_area[0] - obstacle[0], center_point_of_area[1] - obstacle[1])

    if dist == 0.0:
        return True

    area_VEC = np.array([
        m.cos(yaw - m.radians(90.0)), m.sin(yaw - m.radians(90.0))
    ])

    ob_VEC = np.array([
        obstacle[0] -
        center_point_of_area[0], obstacle[1] - center_point_of_area[1]
    ])

    theta = m.acos(np.dot(area_VEC, ob_VEC) /
                   (np.hypot(area_VEC[0], area_VEC[1]) * np.hypot(ob_VEC[0], ob_VEC[1])))
# 3333
    x_dist = abs(dist * m.sin(theta))
    y_dist = abs(dist * m.cos(theta))

    if x_dist <= scale_x / 2.0 and y_dist <= scale_y / 2.0:
        # print(x_dist, y_dist)
        return True

    return False


def where_to_park(available_zone):
    available_zone.insert(0, 0)
    available_zone.append(the_number_of_parkinarea+1)
    row = []  # save continuous times
    area_in_a_row = []  # save continuous parking area
    # (temporary list) save continuous parking area
    temp_of_area_in_a_row = [0]
    j = 0  # save old parking area temporary
    temp_number_of_in_a_row = 1  # save the number of continuous parking area

    for i in available_zone:
        if i == 0:
            continue

        if i == j + 1:
            if j not in temp_of_area_in_a_row:
                temp_of_area_in_a_row.append(j)
            temp_number_of_in_a_row += 1
            temp_of_area_in_a_row.append(i)
            j = i

        else:
            if temp_number_of_in_a_row == [0]:
                temp_of_area_in_a_row = []
                continue
            row.append(temp_number_of_in_a_row)
            area_in_a_row.append(temp_of_area_in_a_row)
            temp_number_of_in_a_row = 1
            temp_of_area_in_a_row = []
            j = i
    row.append(temp_number_of_in_a_row)
    area_in_a_row.append(temp_of_area_in_a_row)

    if max(row) == 1:
        result = available_zone[1]

    else:
        Max = max(row)
        loc_of_Max = row.index(Max)
        candidate_area = area_in_a_row[loc_of_Max]
        print('row', row)
        print('area_in_a_row', area_in_a_row)
        print('candidate', candidate_area)
        print('len', len(candidate_area)/2.0)
        print('index', int(m.ceil(len(candidate_area)/2.0))-1)
        result = candidate_area[int(m.ceil(len(candidate_area)/2.0))-1]
        if result == 0:
            result = 1
        elif result == 7:
            result = 6

    return result


def parseMarker(id, position, duration=1):
    marker = Marker()

    marker.header.frame_id = "map"
    marker.header.stamp = rospy.Time.now()

    marker.pose.position.x = position[0]
    marker.pose.position.y = position[1]
    marker.pose.position.z = 0
    marker.pose.orientation = yaw
    marker.scale.x = scale_x
    marker.scale.y = scale_y

    marker.color = ColorRGBA(0., 0., 1., 5.0)

    marker.type = 5
    marker.id = id
    marker.ns = str(id)
    marker.lifetime = Duration(secs=duration)

    return marker


def markerCallback(msg):
    global parking_areas
    global list_of_center_point_list
    global yaw
    global scale_y
    global scale_x

    list_of_center_point_list = []

    for marker in msg.markers:

        point = marker.pose.position
        orientation = marker.pose.orientation
        scale = marker.scale
        scale_y = scale.y
        scale_x = scale.x
        Parking_area = ParkingArea(
            x=point.x, y=point.y, quat=orientation, w=scale.y, h=scale.x)

        parking_areas.append(Parking_area.parseArray().tolist())

        center_point_list = [point.x, point.y]  # 주차 라인 중앙 점 좌표
        list_of_center_point_list.append(
            center_point_list)  # 주차 라인 중앙 점 좌표 list

    _, _, yaw = euler_from_quaternion(
        [orientation.x, orientation.y, orientation.z, orientation.w])

    rospy.loginfo("Subscribe parking area MarkerArray")

# FOR random_obstacle


'''def obstacleCallback(msg):
    # 3333
    for marker in msg.markers:
        point = marker.pose.position
        list_of_obstacle.append([point.x, point.y])

    rospy.loginfo("Subscribe obstacle MarkerArray")'''


# FOR adaptive_clustering
def obstacleCallback(msg):
    for pose in msg.poses:
        temp_x = pose.position.x
        temp_y = pose.position.y
        list_of_obstacle.append([temp_x, temp_y])


def SequenceCallback(msg):
    global Sequence
    Sequence = msg.data


if __name__ == "__main__":
    rospy.init_node("target_selector")

    global list_of_obstacle
# 3
    list_of_obstacle = []
    parking_areas = []
    list_of_center_point_list = []
    yaw, scale_x, scale_y = 0, 2.5, 5.0
    Sequence = None

    # state = State("/odometry/kalman")
    parking_areas = []
    obstacle_zone = []

    # for adaptive clustering
    rospy.wait_for_message("/obstacle_around_parking_areas", PoseArray)

    # for random
    #rospy.wait_for_message("/obstacle_around_parking_areas", MarkerArray)

    target_zone_pub = rospy.Publisher('/target_zone', Int16, queue_size=1)

    marker_sub = rospy.Subscriber(
        "/parking_areas", MarkerArray, callback=markerCallback)

    # FOR adaptive_clustering
    obstacle_sub = rospy.Subscriber(
        "/obstacle_around_parking_areas", PoseArray, callback=obstacleCallback)

    parking_sequence_sub = rospy.Subscriber(
        '/parking_sequence', Int32, callback=SequenceCallback)

    # FOR random_obstacle
    '''obstacle_sub = rospy.Subscriber(
        "/obstacle_around_parking_areas", MarkerArray, callback=obstacleCallback)'''

    sleep(1.0)

    # center_point_list = [point.x, point.y]

    hz = 1.
    freq = 1 / hz

r = rospy.Rate(hz)
while not rospy.is_shutdown():
    print('It is running')

    if Sequence < 2:
        for ob in list_of_obstacle:
            for i, area in enumerate(list_of_center_point_list):
                # checkIsInParking(obstacle, center_point_of_area)
                TorF = checkIsInParking(ob, area)
                if TorF == True and i+1 not in obstacle_zone:
                    obstacle_zone.append(i+1)

        for ob_zone in obstacle_zone:
            #####################################
            try:
                All_of_parking_area.remove(ob_zone)
            except:
                pass

    elif Sequence == 2:

        print(list_of_obstacle)

        target_zone = where_to_park(All_of_parking_area)

        # parking_zone = where_to_park(available_zone)
        target_zone_msg = Int16()
        target_zone_msg.data = target_zone

        target_zone_pub.publish(target_zone_msg)
        print('result', target_zone)
    else:
        pass
    r.sleep()