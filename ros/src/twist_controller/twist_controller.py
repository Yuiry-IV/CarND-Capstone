import rospy
from pid import PID
from lowpass import LowPassFilter
from yaw_controller import YawController

GAS_DENSITY = 2.858
ONE_MPH = 0.44704

class Controller(object):
    def __init__(self, wheel_radius,
                       wheel_base,
                       steer_ratio,
                       max_lat_accel,
                       max_steer_angle ):
        self.last_time = rospy.get_time()
        # hyperparameters chosen according to lesson 7
        self.velocity_lpf = LowPassFilter(0.5, 0.02)
        # form <b>CarND-PID-Control-Project</b> project
        self.throttle_controller = PID(0.125,0.002,3.1)
        
        self.yaw_controller = YawController( wheel_base,
                steer_ratio,
                0.1,
                max_lat_accel,
                max_steer_angle)

    def control(self, current_vel, linear_vel, angular_vel):
        # calculate steering value
        steering = self.yaw_controller.get_steering( linear_vel, angular_vel, current_vel )
        
        # Filter the high frequncy portion off
        current_vel = self.velocity_lpf.filt(current_vel)
        
        # Calculate parameters for the velocity PID controller
        velocity_error, time_diff = self.get_velocity_error(linear_vel, current_vel)
        
        # Calculate throttle
        throttle = self.throttle_controller.step(velocity_error, time_diff)
        brake = 0.0
        
        return throttle, brake, steering

    def get_velocity_error( self, linear_vel, current_vel ):
        velocity_error = linear_vel - current_vel
        current_time = rospy.get_time()
        time_diff = current_time - self.last_time
        self.last_time = current_time
        return velocity_error, time_diff

    def reset( self ):
        self.throttle_controller.reset()
        self.last_time = rospy.get_time()