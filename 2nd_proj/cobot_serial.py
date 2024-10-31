from pymycobot.mycobot import MyCobot
import time

mc = MyCobot("COM7",115200)
print(mc.get_robot_version())
print(mc.get_system_version())
print(mc.get_robot_id())
print(mc.is_power_on())
print(mc.get_angles())
print(mc.set_basic_output(1,0))
print("1")
print(mc.get_basic_input(1))

