#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
import math

from scipy.spatial import KDTree
import numpy as np
from std_msgs.msg import Int32

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 25 # Number of waypoints we will publish

class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')
        
        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)
        rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)
        
        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)
        # variables
        self.pose = None
        self.base_waypoints = None
        self.waypoints_2d = None
        self.waypoint_tree = None
        self.stopline_wp_idx = -1
        self.current_wp_idx=-1
        # call main loop
        self.loop()

    def loop(self):
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            if self.is_operable():
                self.publish_waypoints()
            rate.sleep()

    def is_operable( self ):
        r = self.pose is not None 
        r = r and self.base_waypoints is not None 
        r = r and self.waypoint_tree is not None
        return r

    def publish_waypoints(self):
        final_lane = self.generate_lane()
        # rospy.logerr( '{:.2f}-{:.2f}'.format(  )
        self.final_waypoints_pub.publish(final_lane)

    def generate_lane (self):
        closest_idx = self.get_closest_waypoint_idx()
        temp_base_waypoints = self.waypoints_norm( closest_idx )
        if self.stopline_wp_idx != -1 and (self.stopline_wp_idx <= (closest_idx+LOOKAHEAD_WPS) ):
            temp_base_waypoints = self.waypoints_slowdown(temp_base_waypoints, closest_idx)
        lane = Lane()
        lane.waypoints = temp_base_waypoints
        if closest_idx != self.current_wp_idx:
            rospy.loginfo( '{:5d}/{:5d}/{:5d}/{:5.2f}/{:5.2f}'.format(
                            closest_idx,
                            len(self.base_waypoints.waypoints),
                            self.stopline_wp_idx,
                            lane.waypoints[0].twist.twist.linear.x,
                            lane.waypoints[-1].twist.twist.linear.x)
                        )
        self.current_wp_idx = closest_idx

        return lane

    def get_closest_waypoint_idx(self):
        query_xy = [self.pose.pose.position.x,
                    self.pose.pose.position.y]
        closest_idx = self.waypoint_tree.query(query_xy,1)[1]
        # Check if the closest is ahead or behind vehicle
        # Equation for hyperplane through closest_coords
        closest_vector = np.array( self.waypoints_2d[closest_idx] )
        prev_vector = np.array( self.waypoints_2d[closest_idx - 1] )
        pose_vector = np.array(query_xy)
        prod = np.dot(closest_vector - prev_vector, 
                     pose_vector - closest_vector)
        if prod > 0:
            closest_idx = (closest_idx + 1) % len(self.waypoints_2d)
        return closest_idx

    def pose_cb(self, msg):
        self.pose = msg

    def waypoints_cb(self, waypoints):
        self.base_waypoints = waypoints
        # Convert waypoints to 2D waypoints
        self.waypoints_2d=[]
        for waypoint in waypoints.waypoints:
            x = waypoint.pose.pose.position.x
            y = waypoint.pose.pose.position.y
            self.waypoints_2d.append([x,y])
        self.waypoint_tree = KDTree(self.waypoints_2d)
        rospy.loginfo(len(waypoints.waypoints))

    def traffic_cb(self, msg):
        self.stopline_wp_idx = msg.data

    def obstacle_cb(self, msg):
        rospy.logerr( "It's optional" )

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist

    def waypoints_norm( self, closest_idx ):
        size = len(self.base_waypoints.waypoints)
        temp = []
        for wpt_idx in range (closest_idx, closest_idx+LOOKAHEAD_WPS):
            wpt = self.base_waypoints.waypoints[ wpt_idx % size ]
            wpt.twist.twist.linear.x = 16.66
            temp.append(wpt)
        if closest_idx < size and closest_idx+LOOKAHEAD_WPS > size:
            rospy.logerr( '{:d}/{:d}'.format(closest_idx, len(temp) ) )
        return temp

    def waypoints_slowdown(self, waypoints, closest_idx):
        temp=[]
        for i, wp in enumerate(waypoints):
            p = Waypoint()
            p.pose = wp.pose
            
            stop_idx = max(self.stopline_wp_idx - closest_idx - 2, 0)
            dist = self.distance(waypoints, i, stop_idx)
            vel = math.sqrt(dist)
            if vel < 1.0:
                vel = 0.0
            p.twist.twist.linear.x = min(vel, wp.twist.twist.linear.x )
            temp.append(p)
        return temp

if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
