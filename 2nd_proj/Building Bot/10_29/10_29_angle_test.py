from pymycobot import MyCobot320

# MyCobot 설정
mc = MyCobot320('COM3', 115200)

# print(mc.get_angles()[5])
mc.send_angle(6, -10, 10)