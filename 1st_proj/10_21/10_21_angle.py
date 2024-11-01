import cv2
import imutils
import socket
import numpy as np
import time
import base64
import threading
from pymycobot.myagv import MyAgv

class customAgv(MyAgv):
    def __basic_move_control(self, *genre, timeout = 5):
        t = time.time()
        self.__movement = True
        while time.time() - t < timeout and self.__movement is True:
            self._mesg(*genre)
            time.sleep(0.1)

    def go_ahead_custom(self, speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128 + speed, 128, 128, timeout=timeout)

    def pan_left_custom(self,speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("pan_right_speed must be between 1 and 127")
        self.__basic_move_control(128, 128 + speed, 128, timeout=timeout)
        
    def pan_right_custom(self,speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("pan_right_speed must be between 1 and 127")
        self.__basic_move_control(128, 128 - speed, 128, timeout=timeout)
        
    def clockwise_rotation_custom(self, speed: int, timeout=5):
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 - speed, timeout=timeout)

    def counterclockwise_rotation_custom(self, speed: int, timeout=5):
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 + speed, timeout=timeout)

mc=customAgv('/dev/ttyAMA2',115200)

mc.clockwise_rotation_custom(1)