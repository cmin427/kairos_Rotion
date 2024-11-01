
import cv2
import numpy as np
from pymycobot import MyCobot320
import time

# MyCobot 설정
mc = MyCobot320('COM3', 115200)

# mc.set_basic_output(1,0)
# time.sleep(2)
# mc.set_basic_output(1,1)
# time.sleep(3)

# while True:
#     mc.sync_send_angles([0,0,0,0,0,0],40)
#     time.sleep(1)

#     if mc.get_basic_input(1)==0:
#         mc.sync_send_angles([15,0,0,0,0,0],40)
#         print(f"get_basic_input의 값은 : {mc.get_basic_input(1)}")
#         time.sleep(1)
        
#     if mc.get_basic_input(1)!=0:
#         print(f"get_basic_input의 값은 : {mc.get_basic_input(1)}")
#         pass
#         time.sleep(1)
        
while True:
    # mc.set_basic_output(1,0)
    mc.set_basic_output(1,1)
    time.sleep(7)
    
    mc.set_basic_output(1,0)
    time.sleep(7)
    # mc.get_basic_input
