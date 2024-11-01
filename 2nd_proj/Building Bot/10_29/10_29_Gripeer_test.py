from pymycobot.mycobot import MyCobot
from pymycobot import MyCobot320
import time
import math

# MyCobot 설정
mc = MyCobot320('COM3', 115200)

print('OPEN')
mc.set_eletric_gripper(1)  # 그립퍼 전원 켜기
mc.set_gripper_value(100, 20)  # 그립퍼 열기
time.sleep(2)

mc.set_gripper_calibration()
mc.set_gripper_mode(0)
mc.init_eletric_gripper()
time.sleep(1) 

mc.set_eletric_gripper(1)  # 그립퍼 전원 켜기
mc.set_gripper_value(20, 20)  # 그립퍼 열기
print('OPEN')
time.sleep(2)

mc.set_eletric_gripper(0)
mc.set_gripper_value(0,20)
print('CLOSE')
time.sleep(2)