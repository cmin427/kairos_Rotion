from pymycobot.myagv import MyAgv
import time 


class customAgv(MyAgv):
    def __basic_move_control(self, *genre, timeout = 5):

 
 
        t = time.time()
        self.__movement = True
        while time.time() - t < timeout and self.__movement is True:
            self._mesg(*genre)
            time.sleep(0.05)

    def go_ahead_custom(self, speed: int, timeout: int = 5):
            """
            Control the car to move forward. 
            Send control commands every 100ms. 
            with a default motion time of 5 seconds.

            Args:
                speed (int): 1 ~ 127 is forward.
                timeout (int): default 5 s.
            """
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
        """
        Control the car to rotate clockwise. 
        Send control commands every 100ms. with a default motion time of 5 seconds
        
        Args:
            speed (int): 1 ~ 127
            timeout (int): default 5 s.
        """
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 - speed, timeout=timeout)

    def counterclockwise_rotation_custom(self, speed: int, timeout=5):
        """
        Control the car to rotate counterclockwise. 
        Send control commands every 100ms. with a default motion time of 5 seconds
        Args:
            speed (int): 1 ~ 127
            timeout (int): default 5 s.
        """
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 + speed, timeout=timeout)







    # def forward_right(self,speed: int, timeout: int = 5): #제대로 안됨
    #     if not (0 < speed < 128):
    #         raise ValueError("pan_left_speed must be between 1 and 127")
    #     self.__basic_move_control(128+speed, 128 + speed, 128, timeout=timeout)

mc=customAgv('/dev/ttyAMA2',115200)


        
    
        


for n in range(50):
    mc.pan_left_custom(1,0.1)
    time.sleep(1)