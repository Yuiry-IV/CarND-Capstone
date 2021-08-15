import rospy
from pid import PID
from lowpass import LowPassFilter
from yaw_controller import YawController

GAS_DENSITY = 2.858
ONE_MPH = 0.44704

class Controller(object):
    def __init__(self, vehicle_mass,
                       decel_limit,
                       wheel_radius,
                       wheel_base,
                       steer_ratio,
                       max_lat_accel,
                       max_steer_angle ):
        
        # hyperparameters chosen according to lesson 7
        # https://youtu.be/kdfXo6atphY?t=317
        tau = 0.5 # 1/(2*Pi*tau) => cutoff frequency
        ts = 0.02 # sample time
        self.velocity_lpf = LowPassFilter(tau, ts)
        
        # hyperparameters chosen according to lesson 7
        # https://youtu.be/kdfXo6atphY?t=317
        self.throttle_controller = PID(0.3, 0.1, 0.0, 0.0, 0.2)
        
        self.yaw_controller = YawController( wheel_base,
                steer_ratio,
                0.1,
                max_lat_accel,
                max_steer_angle)
                
        self.vehicle_mass = vehicle_mass
        self.decel_limit = decel_limit
        self.whell_radius = wheel_radius
        
        self.last_time = rospy.get_time()

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
        
        # according to lesson 7
        # https://youtu.be/kdfXo6atphY?t=472
        if linear_vel == 0.0 and current_vel < 0.1:
            throttle = 0.0
            brake = 700 # N*m - to hols the car in place if we are stopped at a light. Accel. ~ 1m/s^2
        elif throttle < 0.1 and velocity_error < 0.0:
            throttle = 0.0
            decel = max( velocity_error, self.decel_limit )
            brake = abs(decel) * self.vehicle_mass * self.whell_radius # Torque N*m
        
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
