from pymycobot import MyCobot320
import time

mc = MyCobot320("COM7",115200)
# print(mc.get_robot_version())
# print(mc.get_system_version())
# print(mc.get_robot_id())
# print(mc.is_power_on())
# print(mc.get_angles())
# print(mc.set_basic_output(1,0))
# print("1")
# print(mc.get_basic_input(1)==0)

cnt = 0

while True:
    if mc.get_basic_input(1) == 0:
        # print("===")
        pass
    if mc.get_basic_input(2) != 0:
        print(cnt,": else")
    cnt += 1
    # print(mc.get_basic_input(1))
    


