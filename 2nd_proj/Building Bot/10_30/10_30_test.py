from pymycobot import MyCobot320
import time

# MyCobot 설정
mc = MyCobot320('COM3', 115200)

mc.sync_send_coords([29, -133, 250, -170, 2.29, 84.92], 20, 0)
time.sleep(5)

mc.sync_send_angles([0,0,0,0,0,0],20)
time.sleep(2)

# mc.sync_send_coords([(-80.9), (-102.3), 346, (-170), 17.77, 87.55], 40, 0)
# print('안정된 위치로 이동')
# time.sleep(2)

# mc.send_angle(6, -20, 10)
# time.sleep(3)

# print(mc.get_coords())