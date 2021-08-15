from styx_msgs.msg import TrafficLight
import numpy as np
import cv2 as cv

class TLClassifier(object):
    def __init__(self):
        self.lower = np.array([  0,   0, 200])
        self.upper = np.array([100, 100, 255])

    def get_classification(self, image):
        """Determines the color of the traffic light in the image
        Args:
            image (cv::Mat): image containing the traffic light
        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)
        """
        shapeMask = cv.inRange(image, self.lower, self.upper)
        if( np.sum(shapeMask)>99 ):
            return TrafficLight.RED
        return TrafficLight.UNKNOWN
