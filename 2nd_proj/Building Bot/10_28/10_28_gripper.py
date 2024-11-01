from pymycobot import MyCobot320
import time

print('그리퍼 최대로 열어주세요 10초 드립니다')
time.sleep(10)
mc = MyCobot320('COM3',115200)

mc.set_gripper_calibration()
mc.set_gripper_mode(0)
mc.init_eletric_gripper()
time.sleep(1)

print('Gripper Mode' + str(mc.get_gripper_mode()))

print('OPEN')
mc.set_eletric_gripper(1)
mc.set_gripper_value(100,20)
time.sleep(2)

print('CLOSE')
mc.set_eletric_gripper(0)
mc.set_gripper_value(0,20)
time.sleep(2)

print('arm init')
mc.send_angles([0,0,0,0,0,0],20) # 5. 원점 = origin
time.sleep(3)

mc.set_eletric_gripper(1)
print('OPEN')
mc.set_gripper_value(100,20)
time.sleep(2)