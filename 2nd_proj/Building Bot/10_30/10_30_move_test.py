'''
수정된 사항
1. mc.send_coords()를 mc.sync_send_coords()로 변경
2. mc.send_angles()를 mc.sync_send_angles()로 변경
3. move_sort_location(mc, location_index)으로 A지점에 쌓는 블럭 3개를 단순화 했음
'''

'''
추가해야 될 사항
1. 블럭을 쌓는 위치 파악
2. B지점, C지점에 대한 위치값과 블럭 쌓는 위치 파악
'''
import cv2
import numpy as np
from pymycobot import MyCobot320
import time

# MyCobot 설정
mc = MyCobot320('COM3', 115200)

# 그리퍼를 open할 때, 얼마나 벌릴지에 대해 결정하는 함수
def custom_gripper(mc, range, speed):
    print('OPEN')
    mc.set_eletric_gripper(1)  # 그립퍼 전원 켜기
    mc.set_gripper_value(range, speed)  # 그립퍼 열기
    time.sleep(2)

# 그리퍼를 최대한으로 open 하는 함수
def open_gripper(mc):
    print('OPEN')
    mc.set_eletric_gripper(1)  # 그립퍼 전원 켜기
    mc.set_gripper_value(100, 20)  # 그립퍼 열기
    time.sleep(2)

# 그리퍼를 최대한으로 close 하는 함수
def close_gripper(mc):
    print('CLOSE')
    mc.set_eletric_gripper(0)
    mc.set_gripper_value(0,20)
    time.sleep(2)

# 그리퍼를 사용하기 위해선 처음에 캘리브레이션 하기 위한 함수
def calibration_gripper(mc):
    mc.set_gripper_calibration()
    mc.set_gripper_mode(0)
    mc.init_eletric_gripper()
    time.sleep(1)   

# mc.sync_send_angles([0, 0, 0, 0, 0, 0], 20) : 원점으로 이동하는함수 -> 로봇암은 원점으로 이동해야 이동에 제약이 사라지는 경우가 많으므로 적용했음
def move_origin(mc):
    mc.sync_send_angles([0, 0, 0, 0, 0, 0], 40)
    print("원점으로 이동")
    time.sleep(2)

# 컨베이어 벨트를 따라서 블럭이 떨어지는 곳으로 이동하는 함수
def move_block(mc):
    mc.sync_send_angles([(-4.04), (-30.23), 62, 57.3, (-87.8), 0.96], 30)
    print("BOX 위치로 이동")
    time.sleep(2)

# 블럭의 중심좌표값을 통해 로봇팔이 움직일 위치 계산하는 함수
def move_center_block(mc,box_center):
    robot_x, robot_y = get_robot_position(box_center)
    mc.sync_send_coords([robot_x, robot_y, 300, -170, 2.29, 84.92], 20, 0)
    print(f"로봇팔 위치로 이동: ({robot_x}, {robot_y})")
    time.sleep(5)

# 한번에 낮은 z 값으로 이동하면 제대로 집지를 못하므로 블럭의 중심좌표 값으로 이동한 뒤에 z 값만을 내려서 로봇암을 하강시키는 함수
def move_down(mc):
    robot_x, robot_y = get_robot_position(box_center)
    # mc.sync_send_coords([robot_x, robot_y, 235, -170, 2.29, 84.92], 20, 0)
    x_coord = mc.get_coords()[0]
    y_coord = mc.get_coords()[1]
    rx_coord = mc.get_coords()[3]
    ry_coord = mc.get_coords()[4]
    rz_coord = mc.get_coords()[5]
    mc.sync_send_coords([x_coord, y_coord, 240, rx_coord, ry_coord, rz_coord], 20, 0)
    print(f"로봇팔 위치로 이동: ({robot_x}, {robot_y})")
    time.sleep(3)

# 컨베이어 벨트를 따라서 블럭이 떨어지는 곳으로 이동해서 도착한 블럭이 돌아가는 경우가 많아서 돌아간 angle 만큼 그리퍼를 돌리는 함수
def turn_gripper(mc):
    print(angle)
    # s6의 angle 값을 받아와서 보정하기, -: 반시계 회전
    joint6_angle = mc.get_angles()[5]
    mc.send_angle(6, joint6_angle+angle, 10)
    time.sleep(3)

# 컨베이어 벨트에서 잡은 뒤에 컨베이어 벨트에 걸리는 것을 방지하는 위치로 이동하는 함수
def move_block_rear(mc):
    mc.sync_send_coords([(-80.9), (-102.3), 346, (-170), 17.77, 87.55], 40, 0)
    print('안정된 위치로 이동')
    time.sleep(2)
    
# 블럭을 쌓는 곳으로 이동하는 함수
def move_center_sort(mc):
    mc.sync_send_angles([(-40.42),11.77,(-94.92),(-5.44),96.67,15.02],30)
    print('중앙')
    time.sleep(5)

# gripper 설정
open_gripper(mc)
calibration_gripper(mc) # 코드를 처음 실행할때만 넣으면 됨
close_gripper(mc)


# 1번째
# 원점 이동
move_origin(mc)

# 그리퍼 열음
custom_gripper(mc, 50, 20)

# 그리퍼 닫음
close_gripper(mc)

# 쌓는 위치의 중간 위치로 이동
move_center_sort(mc)

# 첫 번째 지점
mc.sync_send_coords([128.7, (-333.7), 177.2, (-170), 0.71, (-159.42)], 20, 0)
print('1번째 지점으로 이동')
time.sleep(5)

# 그리퍼 열음
open_gripper(mc)

# 쌓는 위치의 중간 위치로 이동
move_center_sort(mc)

# 그리퍼 닫음
close_gripper(mc)


# 2번째
# 원점 이동
move_origin(mc)

# 그리퍼 열음
custom_gripper(mc, 50, 20)

# 그리퍼 닫음
close_gripper(mc)

# 쌓는 위치의 중간 위치로 이동
move_center_sort(mc)

# 두 번째 지점
mc.sync_send_coords([128.7, (-333.7), 206.2, (-170), 0.71, (-159.42)], 20, 0)
print('A 지점의 두번째 블록 쌓는중')
time.sleep(5)

# 그리퍼 열음
open_gripper(mc)

# 쌓는 위치의 중간 위치로 이동
move_center_sort(mc)

# 그리퍼 닫음
close_gripper(mc)



# 3번째
# 원점 이동
move_origin(mc)

# 그리퍼 열음
custom_gripper(mc, 50, 20)

# 그리퍼 닫음
close_gripper(mc)

# 쌓는 위치의 중간 위치로 이동
move_center_sort(mc)

# 세 번째 지점
mc.sync_send_coords([128.7, (-333.7), 244.2, (-170), 0.71, (-159.42)], 20, 0)
print('A 지점의 세번째 블록 쌓는중')
time.sleep(5)

# 그리퍼 열음
open_gripper(mc)

# 쌓는 위치의 중간 위치로 이동
move_center_sort(mc)

# 그리퍼 닫음
close_gripper(mc)