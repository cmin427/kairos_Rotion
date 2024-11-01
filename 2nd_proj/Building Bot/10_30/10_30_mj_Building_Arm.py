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
    time.sleep(1)

# 그리퍼를 최대한으로 open 하는 함수
def open_gripper(mc):
    print('OPEN')
    mc.set_eletric_gripper(1)  # 그립퍼 전원 켜기
    mc.set_gripper_value(100, 20)  # 그립퍼 열기
    time.sleep(1)

# 그리퍼를 최대한으로 close 하는 함수
def close_gripper(mc):
    print('CLOSE')
    mc.set_eletric_gripper(0)
    mc.set_gripper_value(0,20)
    time.sleep(1)

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
    time.sleep(1)

# 컨베이어 벨트를 따라서 블럭이 떨어지는 곳으로 이동하는 함수
def move_block(mc):
    mc.sync_send_angles([(-4.04), (-30.23), 62, 57.3, (-87.8), 0.96], 40)
    print("BOX 위치로 이동")
    time.sleep(1)

# 블럭의 중심좌표값을 통해 로봇팔이 움직일 위치 계산하는 함수
def move_center_block(mc,box_center):
    robot_x, robot_y = get_robot_position(box_center)
    mc.sync_send_coords([robot_x, robot_y, 250, -170, 2.29, 84.92], 20, 0)
    print(f"로봇팔 위치로 이동: ({robot_x}, {robot_y})")
    time.sleep(3)

# 한번에 낮은 z 값으로 이동하면 제대로 집지를 못하므로 블럭의 중심좌표 값으로 이동한 뒤에 z 값만을 내려서 로봇암을 하강시키는 함수
def move_down(mc):
    robot_x, robot_y = get_robot_position(box_center)
    # mc.sync_send_coords([robot_x, robot_y, 235, -170, 2.29, 84.92], 20, 0)
    x_coord = mc.get_coords()[0]
    y_coord = mc.get_coords()[1]
    rx_coord = mc.get_coords()[3]
    ry_coord = mc.get_coords()[4]
    rz_coord = mc.get_coords()[5]
    mc.sync_send_coords([x_coord, y_coord, 210, rx_coord, ry_coord, rz_coord], 20, 0)
    print(f"로봇팔 위치로 이동: ({robot_x}, {robot_y})")
    time.sleep(3)

# 컨베이어 벨트를 따라서 블럭이 떨어지는 곳으로 이동해서 도착한 블럭이 돌아가는 경우가 많아서 돌아간 angle 만큼 그리퍼를 돌리는 함수
def turn_gripper(mc):
    print(angle)
    # s6의 angle 값을 받아와서 보정하기, -: 반시계 회전
    joint6_angle = mc.get_angles()[5]
    mc.send_angle(6, joint6_angle+angle, 20)
    time.sleep(2)

# 컨베이어 벨트에서 잡은 뒤에 컨베이어 벨트에 걸리는 것을 방지하는 위치로 이동하는 함수
def move_block_rear(mc):
    mc.sync_send_coords([(-80.9), (-102.3), 346, (-170), 17.77, 87.55], 40, 0)
    print('안정된 위치로 이동')
    time.sleep(1)
    
# 블럭을 쌓는 곳의 안정한 곳으로 이동하는 함수
def move_center_sort(mc):
    mc.sync_send_angles([(-40.42),11.77,(-94.92),(-5.44),96.67,15.02],40)
    print('중앙')
    time.sleep(2)

# A 블럭 3개를 정리하는 위치를 저장한 함수
def move_sort_location_A(mc, block_count):
    # 각 위치에 맞는 각도로 이동 설정
    if block_count == 0:
        # 첫 번째 지점
        mc.sync_send_coords([128.7, (-333.7), 177.2, (-170), 0.71, (-159.42)], 20, 0)
        print('A 지점의 첫번째 블록 쌓는중')
        time.sleep(5)
    elif block_count == 1:
        # 두 번째 지점
        mc.sync_send_coords([128.7, (-333.7), 206.2, (-170), 0.71, (-159.42)], 20, 0)
        print('A 지점의 두번째 블록 쌓는중')
        time.sleep(5)
    elif block_count == 2:
        # 세 번째 지점
        mc.sync_send_coords([128.7, (-333.7), 234.2, (-170), 0.71, (-159.42)], 20, 0)
        print('A 지점의 세번째 블록 쌓는중')
        time.sleep(5)
        
# B 블럭 3개를 정리하는 위치를 저장한 함수
def move_sort_location_B(mc, block_count):
    # 각 위치에 맞는 각도로 이동 설정
    if block_count == 0:
        # 첫 번째 지점
        mc.sync_send_coords([204.8, (-274.8), 177.2, (-170), 0.71, (-159.42)], 20, 0)
        print('B 지점의 첫번째 블록 쌓는중')
        time.sleep(5)
    elif block_count == 1:
        # 두 번째 지점
        mc.sync_send_coords([204.8, (-274.8), 206.2, (-170), 0.71, (-159.42)], 20, 0)
        print('B 지점의 두번째 블록 쌓는중')
        time.sleep(5)
    elif block_count == 2:
        # 세 번째 지점
        mc.sync_send_coords([204.8, (-274.8), 234.2, (-170), 0.71, (-159.42)], 20, 0)
        print('B 지점의 두번째 블록 쌓는중')
        time.sleep(5)
        
# C 블럭 3개를 정리하는 위치를 저장한 함수
def move_sort_location_C(mc, block_count):
    # 각 위치에 맞는 각도로 이동 설정
    if block_count == 0:
        # 첫 번째 지점
        mc.sync_send_coords([275.7, (-210.9), 177.2, (-170), 0.71, (-159.42)], 20, 0)
        print('C 지점의 첫번째 블록 쌓는중')
        time.sleep(5)
    elif block_count == 1:
        # 두 번째 지점
        mc.sync_send_coords([275.7, (-210.9), 206.2, (-170), 0.71, (-159.42)], 20, 0)
        print('C 지점의 두번째 블록 쌓는중')
        time.sleep(5)
    elif block_count == 2:
        # 세 번째 지점
        mc.sync_send_coords([275.7, (-210.9), 234.2, (-170), 0.71, (-159.42)], 20, 0)
        print('C 지점의 두번째 블록 쌓는중')
        time.sleep(5)

def move_trash(mc):
    mc.sync_send_coords([319.1, (-27.5), 221.5, 170, 1.19, (-86.75)], 30, 0)
    print('버리는 위치로 이동')
    time.sleep(2)

# 보간 계수 계산 함수 (앞서 계산된 중심값과 로봇팔 좌표값으로부터)
center_points = np.array([
    # [268, 211], [296,315], [310, 268], [267, 207], [221, 238], 
    # [203, 229], [314, 335], [296, 232], [256, 285], [278, 188],
    # [395, 307], [150, 321]
    [254, 266], [280, 226], [263, 235], [249, 199], [297, 253], 
    [293, 280], [251, 240], [236, 203], [254, 194], [293, 257]
])
robot_positions = np.array([
    # [-35, -190], [-50, -130], [-55, -163], [-37, -188], [-15, -179], 
    # [0, -179], [-58, -126], [-47, -178], [-28, -154], [-38, -200],
    # [-100, -133], [29, -133]
    [-51, -160], [-55, -188], [-47, -180], [-41, -201], [-67, -173], 
    [-60, -160], [-43, -179], [-34, -198], [-48, -200], [-63, -172]
])

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

    # 색상 별 마스크 영역
    mask_green = cv2.inRange(frame, (60,75,80), (100,255,255))      # green
    mask_green = np.repeat(mask_green[:,:,np.newaxis],3,-1)
    mask_red1 = cv2.inRange(frame, (0,100,100), (10,255,255))     # red
    mask_red2 = cv2.inRange(frame, (170,100,100), (180,255,255))
    mask_red1 = np.repeat(mask_red1[:,:,np.newaxis],3,-1)
    mask_red2 = np.repeat(mask_red2[:,:,np.newaxis],3,-1)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_yellow = cv2.inRange(frame, (10,100,80), (30,255,255))     # yellow
    mask_yellow = np.repeat(mask_yellow[:,:,np.newaxis],3,-1)
    mask_purple = cv2.inRange(frame, (130,85,51), (150,255,255))     # purple
    mask_purple = np.repeat(mask_purple[:,:,np.newaxis],3,-1)

    # 마스크랑 겹치는 영역
    dst1 = cv2.bitwise_and(frame,mask_green)
    dst2 = cv2.bitwise_and(frame,mask_red)
    dst3 = cv2.bitwise_and(frame,mask_yellow)
    dst4 = cv2.bitwise_and(frame,mask_purple)

    green_sum = np.sum(dst1)
    red_sum = np.sum(dst2)
    yellow_sum = np.sum(dst3)
    purple_sum = np.sum(dst4)

    # 제일 큰 값으로 반환
    if max(green_sum, red_sum, yellow_sum, purple_sum) == green_sum:
        color= 'Green'
    elif max(green_sum, red_sum, yellow_sum, purple_sum) == red_sum:
        color= 'Red'
    elif max(green_sum, red_sum, yellow_sum, purple_sum) == yellow_sum:
        color= 'Yellow'
    else:
        color='Purple'

    if color == 'Red':
        lower1 = np.array([0,100,100]) 
        upper1 = np.array([10,255,255])
        lower2 = np.array([170,100,100]) 
        upper2 = np.array([180,255,255])
        # mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        frame1 = cv2.inRange(frame, lower1, upper1)
        frame2 = cv2.inRange(frame, lower2, upper2)
        frame = cv2.bitwise_or(frame1, frame2)
    elif color == 'Green':
        lower = np.array([60,75,80])
        upper = np.array([100,255,255]) 
        frame = cv2.inRange(frame, lower, upper)
    elif color == 'Yellow':
        lower = np.array([10,100,80])
        upper = np.array([30,255,255]) 
        frame = cv2.inRange(frame, lower, upper)
    else:
        lower = np.array([130,85,51])
        upper = np.array([150,255,255])
        frame = cv2.inRange(frame, lower, upper)

        # 바이너리로 반환
    return frame,color

# 카메라 및 초기 설정
cap = cv2.VideoCapture(1)

# gripper 설정
open_gripper(mc)
calibration_gripper(mc) # 코드를 처음 실행할때만 넣으면 됨
close_gripper(mc)


# 이동 완료 플래그
completed = False

block_count_in_location_A=0
block_count_in_location_B=0
block_count_in_location_C=0

# 메인 동작 반복
'''
그리퍼 열음 -> 캘리블이션 -> 그리퍼 닫음 -> 원점으로 이동 -> 블럭으로 이동

LOOP
원점 이동 -> 블럭의 중심값의 위치로 로봇암 이동 -> 그리퍼 열음 -> 로봇암 하강 -> 로봇암 돌음 -> 그리퍼 닫음
-> 뒤로 후진 -> 쌓는 위치의 중간 위치로 이동 -> 쌓는 위치로 이동 -> 그리퍼 열음 -> 쌓는 위치의 중간 위치로 이동 -> 그리퍼 닫음
'''

while not completed:
        
    
    # 원점 이동
    move_origin(mc)
    
    # 블록 촬영하는 위치로 이동
    move_block(mc)
    
    #블록 촬영 후 화면 상의 박스 중심 좌표 계산
    ret, frame = cap.read()
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masked, color = color_detect(frame_hsv)
    median = cv2.medianBlur(masked, 15)
    contours, _ = cv2.findContours(median, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    box_center = None
    
    for cont in contours:
        rect = cv2.minAreaRect(cont)
        box_center = (int(rect[0][0]), int(rect[0][1]))
        angle = int(rect[2])
        print(f'처음 angle {angle}')
        if angle > 45:
            angle = -int(90-angle)
        print(f'계산된 angle {angle}')
        break  # 첫 번째 박스만 처리

    if box_center:
        print(f'BOX의 중심좌표값 : {box_center}')
        cv2.circle(frame, box_center, 5, (255, 0, 0), -1)
        cv2.imwrite('frame.jpg', frame)
        cv2.imwrite('masked.jpg', median)
        

        
    #원활한 이동을 위해 원점으로 재이동
    move_origin(mc)

    # 블럭의 중심값의 위치로 로봇암 이동
    move_center_block(mc,box_center)
    
    # 그리퍼 열음
    custom_gripper(mc, 70, 20)
    
    # 로봇암 돌음
    turn_gripper(mc)
    
    # 로봇암 하강
    move_down(mc)

    # 그리퍼 닫음
    close_gripper(mc)
    
    # 뒤로 후진
    move_block_rear(mc)
    
    # 쌓는 위치의 중간 위치로 이동
    move_center_sort(mc)
    
    if color=='Green':
        move_sort_location_A(mc, block_count_in_location_A)
        block_count_in_location_A+=1
        print(f"{block_count_in_location_A} location_A에 대한 값: {mc.get_coords()}")
        
    elif color=='Red':           
        move_sort_location_B(mc, block_count_in_location_B)
        block_count_in_location_B+=1
        print(f"{block_count_in_location_B} location_B에 대한 값: {mc.get_coords()}")
        
    elif color=='Purple':
        move_sort_location_C(mc, block_count_in_location_C)
        block_count_in_location_C+=1
        print(f"{block_count_in_location_C} location_C에 대한 값: {mc.get_coords()}")
        
    elif color=='Yellow':
        move_trash(mc)
    

    
    # 그리퍼 열음
    open_gripper(mc)
    
    # 쌓는 위치의 중간 위치로 이동
    move_center_sort(mc)
    
    # 그리퍼 닫음
    close_gripper(mc)
            

       
    if block_count_in_location_A==3 and block_count_in_location_B==3 and block_count_in_location_C==3:
        # 작업 완료 표시
        completed = True
        print('모든 지점에 블럭 쌓기 완료')

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()