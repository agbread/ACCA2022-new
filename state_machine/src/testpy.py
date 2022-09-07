import rospy
from enum import Enum
from time import sleep

class State(Enum):
    DRIVING = 0
    TRAFFIC = 1
    DELIVERY = 2
    STATIC = 3
    DYNAMIC = 4
    PARKING = 5
    END = 9


class TEST:
    def __init__(self):
        self.state = State.DRIVING        

    def testing(self):
        sleep(3)
        self.state = State.TRAFFIC
        
        sleep(3)
        self.state = State.STATIC


if __name__ == "__main__":
    rospy.init_node("Test")
    tests = TEST()
    r = rospy.Rate(30)
    
    while not rospy.is_shutdown():
        tests.testing()

        r.sleep()