import cv2
import numpy as np
from pymycobot.mycobot import MyCobot
from pymycobot import MyCobot320
import time
import math

# MyCobot 설정
mc = MyCobot320('COM3', 115200)

# gripper open
def open_gripper(mc):
    print('OPEN')
    mc.set_eletric_gripper(1)  # 그립퍼 전원 켜기
    mc.set_gripper_value(100, 20)  # 그립퍼 열기
    time.sleep(2)

# gripper close
def close_gripper(mc):
    print('CLOSE')
    mc.set_eletric_gripper(0)
    mc.set_gripper_value(0,20)
    time.sleep(2)

# gripper calibration
def calibration_gripper(mc):
    mc.set_gripper_calibration()
    mc.set_gripper_mode(0)
    mc.init_eletric_gripper()
    time.sleep(1)   

# mc.send_angles([0, 0, 0, 0, 0, 0], 20) : 원점으로 이동
def move_origin(mc):
    mc.send_angles([0, 0, 0, 0, 0, 0], 20)
    print("원점으로 이동")
    time.sleep(5)

# 컨베이어 벨트를 따라서 box가 모이는 곳으로 이동
def move_box(mc):
    mc.send_coords([(-75), (-107), 265, (-170), (-5), 170], 20, 0)
    print("BOX 위치로 이동")
    time.sleep(5)

# box를 정리하는 곳으로 이동
def move_sort(mc):
    mc.send_coords([40, -288, 300, -161, -8, -163], 20, 0)
    print("정리대로 이동")
    time.sleep(5)

# gripper 설정
open_gripper(mc)
calibration_gripper(mc)

# 보간 계수 계산 함수 (앞서 계산된 중심값과 로봇팔 좌표값으로부터)
center_points = np.array([[238, 77], [297, 77], [387, 65], [361, 64], [288, 78], [438, 71], [314, 75], [443, 60], [442, 58]])
robot_positions = np.array([[-95, -215], [-120, -215], [-150, -215], [-110, -210], [-160, -215], [-120, -215], [-170, -215], [-115, -180], [-165, -215]])

coeff_x = np.polyfit(center_points[:, 0], robot_positions[:, 0], 1)
coeff_y = np.polyfit(center_points[:, 1], robot_positions[:, 1], 1)

# 카메라에서 검출된 박스의 중심값을 입력받아 로봇팔의 좌표값을 반환하는 함수
def get_robot_position(box_center):
    center_x, center_y = box_center
    robot_x = np.polyval(coeff_x, center_x)
    robot_y = np.polyval(coeff_y, center_y)
    return robot_x, robot_y

# 블록 색상 판별하는 함수
def color_detect(frame):
    mask_green = cv2.inRange(frame, (60,75,80), (100,255,255))      # green
    mask_green = np.repeat(mask_green[:,:,np.newaxis],3,-1)
    mask_red = cv2.inRange(frame, (150,80,80), (180,255,255))     # red
    mask_red = np.repeat(mask_red[:,:,np.newaxis],3,-1)
    mask_yellow = cv2.inRange(frame, (10,100,80), (30,255,255))     # yellow
    mask_yellow = np.repeat(mask_yellow[:,:,np.newaxis],3,-1)
    mask_purple = cv2.inRange(frame, (130,85,51), (150,255,255))     # purple
    mask_purple = np.repeat(mask_purple[:,:,np.newaxis],3,-1)

    dst1 = cv2.bitwise_and(frame, mask_green)
    dst2 = cv2.bitwise_and(frame, mask_red)
    dst3 = cv2.bitwise_and(frame, mask_yellow)
    dst4 = cv2.bitwise_and(frame, mask_purple)

    green_sum = np.sum(dst1)
    red_sum = np.sum(dst2)
    yellow_sum = np.sum(dst3)
    purple_sum = np.sum(dst4)

    if max(green_sum, red_sum, yellow_sum, purple_sum) == green_sum:
        color = 'Green'
    elif max(green_sum, red_sum, yellow_sum, purple_sum) == red_sum:
        color = 'Red'
    elif max(green_sum, red_sum, yellow_sum, purple_sum) == yellow_sum:
        color = 'Yellow'
    else:
        color = 'Purple'

    if color == 'Red':
        lower = np.array([150, 80, 80])
        upper = np.array([180, 255, 255])
    elif color == 'Green':
        lower = np.array([60, 75, 80])
        upper = np.array([100, 255, 255])
    elif color == 'Yellow':
        lower = np.array([10, 100, 80])
        upper = np.array([30, 255, 255])
    else:
        lower = np.array([130, 85, 51])
        upper = np.array([150, 255, 255])

    frame = cv2.inRange(frame, lower, upper)
    return frame

# 카메라 및 초기 설정
cap = cv2.VideoCapture(1)

# robot arm 이동
move_origin(mc)
move_box(mc)

# 이동 완료 플래그
completed = False

while not completed:
    ret, frame = cap.read()
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masked = color_detect(frame_hsv)
    median = cv2.medianBlur(masked, 15)
    contours, _ = cv2.findContours(median, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cv2.imshow('frame', frame)
    box_center = None
    for cont in contours:
        rect = cv2.minAreaRect(cont)
        box_center = (int(rect[0][0]), int(rect[0][1]))
        break  # 첫 번째 박스만 처리

    if box_center:
        print(f'BOX의 중심좌표값 : {box_center}')
        cv2.circle(frame, box_center, 5, (255, 0, 0), -1)

        # 원점으로 돌아가기
        move_origin(mc)
        
        # 중심좌표값을 통해 로봇팔의 위치 계산
        robot_x, robot_y = get_robot_position(box_center)
        mc.send_coords([robot_x, robot_y, 230, -170, -5, 170], 20, 0)
        print(f"로봇팔 위치로 이동: ({robot_x}, {robot_y})")
        time.sleep(5)

        # gripper 설정
        print('Gripper Mode' + str(mc.get_gripper_mode()))
        open_gripper(mc)
        close_gripper(mc)
        
        # robot arm 이동
        move_origin(mc)
        move_sort(mc)

        # gripper 작동
        open_gripper(mc)
        close_gripper(mc)
        
        # 원점으로 돌아가기
        move_origin(mc)
        
        # 이동 완료 플래그 설정
        completed = True
        print('종료')

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
