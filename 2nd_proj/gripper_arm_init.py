from pymycobot.mycobot import MyCobot
import time

mc = MyCobot('COM7',115200)
print('그리퍼 최대로 열어주세요 5초 드립니다')
time.sleep(5)

mc.send_angles([15,0,0,0,0,0],20)
print('arm connected')
mc.set_gripper_calibration()
mc.set_gripper_mode(0)
mc.init_eletric_gripper()
time.sleep(1)
print('Gripper Mode: ' + str(mc.get_gripper_mode()))
mc.set_eletric_gripper(1)
mc.set_gripper_value(100,20)
print('OPEN')
time.sleep(2)
mc.set_eletric_gripper(0)
mc.set_gripper_value(0,20)
print('CLOSE')
time.sleep(2)
mc.send_angles([0,0,0,0,0,0],20) # 5. 원점 = origin
print('arm init')
time.sleep(3)
mc.set_eletric_gripper(1)
mc.set_gripper_value(100,20)
print('OPEN')
time.sleep(2)