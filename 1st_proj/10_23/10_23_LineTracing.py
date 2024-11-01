import cv2
import imutils
import socket
import numpy as np
import time
import math
import base64
import threading
from pymycobot.myagv import MyAgv

# agv 인스턴스 생성
mc=MyAgv('/dev/ttyAMA2',115200)

# 비디오 캡쳐 인스턴스 생성
vid = cv2.VideoCapture(-2)

"""
camera_capture_allowe: 비디오 촬영이 허용되는지. 얘를 그냥 agv가 멈췄을때만 가능한걸로 할지,
아니면 도착 직전에도 찍는게 가능하게 할지? 일단은 그냥 멈췄을때만 찍게함

"""

camera_capture_allowed= not mc.is_agv_moving

time_to_go_ahead_roi_bottom=3.1
time_to_go_ahead_roi_top=2.6

# roi 상에서 화면 가로길이 pan 하는데 걸리는 시간 (속도 1일 때)
pan_move_constant= 1.7

# roi 상에서 1도를 회전하는데 걸리는 시간 (속도 1일 때)
rotate_move_constant= 13/360 

moving_command= "t563 a1b1c0 5" #time 뒤 세자리 초에서 찍었고 앞으로 1 왼쪽으로 1 방향으로 5초만큼 가야할때 명령어
# moving_command="NoLine"
# moving_command="Stop"

# 맨 위와 맨 아래 줄에서 흰색 픽셀들의 무게 중심 구하기
def get_centroid_of_row(binary_image, row):
    white_pixels = np.where(binary_image[row] == 255)[0]
    if len(white_pixels) == 0:
        return None
    centroid = np.mean(white_pixels)
    return int(centroid)

# 두 픽셀을 연결하는 직선 그리기
def draw_line(image, start_point, end_point):
    color = (0, 0, 255)  # 빨간색
    thickness = 2
    cv2.line(image, start_point, end_point, color, thickness)

# 직선이 세로선과 이루는 각도 계산
def calculate_angle(start_point, end_point):
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)
    # 세로선과의 각도이므로 수직선(90도)에서 빼줌
    vertical_angle = 90 - abs(angle_degrees)
    return vertical_angle

def calculate_angle_and_bias(roi):
    
    idx_middle_column=roi.shape[1]//2
    top_row = 0
    bottom_row = roi.shape[0] - 1
    
    top_centroid = get_centroid_of_row(roi, top_row)
    bottom_centroid = get_centroid_of_row(roi, bottom_row)
    # if top_centroid is None or bottom_centroid is None:
    #     print("흰색 픽셀이 부족하여 무게 중심을 계산할 수 없습니다.")
    #     return
    
    top_point = (top_centroid, top_row)
    bottom_point = (bottom_centroid, bottom_row)
    image_with_line = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
    draw_line(image_with_line, top_point, bottom_point)
    
    # 각도 계산
    angle = calculate_angle(top_point, bottom_point)
    top_point_bias=idx_middle_column-top_point
    bottom_point_bias=-idx_middle_column+bottom_point
    
    return angle, top_point_bias, bottom_point_bias
    

    
def cropped_roi_has_straight_line(angle):
    if abs(angle)<5:
        return True
    else:
        return False
def cropped_roi_has_line_in_center(bottom_point_bias,roi_width):
    if (abs(bottom_point_bias)/(roi_width//2))<0.1:
        return True
    else:
        return False
    
def mask_by_yellow(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])
        
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask 
    

# frame 한 장을 입력 받아 적절한 움직임을 계산하여 결과를 문자열로 리턴하는 함수
def process_frame(frame): # "a1b1c0 5" 이렇게만 리턴함
    moving_command_temp="" #빈 문자열
    
    roi=frame[:,frame.shape[1]//3 :(frame.shape[1]//3)*2] # 일단 roi를 가로로 가운데 3분의1만 보는걸로 해둠 
    
    masked_roi=mask_by_yellow(roi)
    cv2.resize(masked_roi,(200, 200), interpolation=cv2.INTER_LINEAR) # 승하님이 해둔거 이식 
    
    middle_row = int(masked_roi.shape[0]*0.4)
    
    bottom_row = masked_roi.shape[0] - 1
    
    
    
    #프레임을 위에서부터 3분할 하기. 
    roi1=masked_roi[:middle_row ,:]

    roi2=masked_roi[middle_row+1:bottom_row ,:]

    
    angle_roi1, top_point_bias_roi1, bottom_point_bias_roi1=calculate_angle_and_bias(roi1)
    angle_roi2, top_point_bias_roi2, bottom_point_bias_roi2=calculate_angle_and_bias(roi2)
    
    
    if cropped_roi_has_straight_line(angle_roi1) and cropped_roi_has_line_in_center(angle_roi1): 
        
        if cropped_roi_has_line_in_center(bottom_point_bias_roi1,roi1.shape[1]) and cropped_roi_has_line_in_center(bottom_point_bias_roi2,roi2.shape[1]):
            
            #화면 끝까지 go ahead 가능할때 
            moving_command_temp=moving_command_temp+f"a1b0c0 {time_to_go_ahead_roi_bottom+time_to_go_ahead_roi_top}"
        else: 
            #화면 중간까지만 go ahead 가능할때
            moving_command_temp=moving_command_temp+f"a1b0c0 {time_to_go_ahead_roi_bottom}"
         
    else:
        if cropped_roi_has_straight_line(roi1):
            # 각도는 비틀어지지 않았는데 치우쳐져 있을때
            
            if bottom_point_bias_roi1<0: #왼쪽으로 치우쳐져 있을 경우 
                moving_command_temp=moving_command_temp+f"a0b1c0 {abs(bottom_point_bias_roi1)*(pan_move_constant/2)}"
  
            else: #오른쪽으로 치우쳐져 있을 경우
                moving_command_temp=moving_command_temp+f"a0b-1c0 {abs(bottom_point_bias_roi1)*(pan_move_constant/2)}"
        else:
            # 각도가 비틀어진 경우
            if angle_roi1 < 0 : # 시계방향으로 비틀어져있는 경우(시계방향으로 돌려야할 경우)
                moving_command_temp=moving_command_temp+f"a0b0c1 {abs(angle_roi1*rotate_move_constant)}"
                
            else: # 반시계 방향으로 비틀어져있는 경우(시계방향으로 돌려야 할 경우)
                moving_command_temp=moving_command_temp+f"a0b0c-1 {abs(angle_roi1*rotate_move_constant)}"
                

    return moving_command_temp

    
    
    


def agv_motor_control():# 주행 방향과 시간을 입력받고 모터를 구동하는 함수
    
    while True:
        
        command_str=moving_command
        if last_command_str == command_str: # 프로토콜이 업데이트 되지 않았을 경우, 
            pass
            # 멈춰야 되는데? 
        else: #프로토콜이 바뀌었을 경우
        
            words = command_str.split()  # 공백 단위로 문자열 분리
            
            if words[0]=="Stop": #프로토콜이 Stop일 경우 
                
                mc.move_control(127,127,127)
                time.sleep(1)
            
                # abcd 프로토콜로 분리하되 -1처럼 두글자도 있으니까 idx of a+1 idx of b-1 사이 문자열 이런식으로 처리 
                
                last_command_str=command_str
            else:
                pass
                


def camera_capture_and_process_command():  # 외부 환경을 촬영하고 적절한 agv 주행 방법을 문자열 형식으로 리턴하는 함수
    while vid.isOpened():
        global moving_command
        
        if camera_capture_allowed:
            _, frame = vid.read()
            t = int((time.time()) * 1000) % 1000  # 숫자로 아이디값 세자리 생성
            moving_command = process_frame(frame)
            moving_command = str(t) + ' ' + moving_command

            ######################################################
            # 영상처리가 너무 느릴시 얘로 교체 
            # t = int((time.time()) * 1000) % 1000
            # moving_command = send_frame_to_client_and_wait(frame) 
            # moving_command = str(t) + ' ' + moving_command
            ######################################################
            
        else:
            # 얘는 time.sleep을 넣는게 나을지 안넣는게 나을지? 일단 아무것도 안하게 함
            pass


            
            
if __name__ == "__main__":

    t1 = threading.Thread(target=camera_capture_and_process_command)
    t2 = threading.Thread(target=agv_motor_control)

    t1.start()
    t2.start()

    # 각 스레드가 종료될 때까지 대기
    t1.join()
    t2.join()