# client#
import cv2, imutils, socket
import numpy as np
import time
import base64
import math

#time_degree_ratio : clockwise를 속도 1로 실행시 1도를 몇초만에 도는지 
time_360_turn=13
time_degree_ratio=time_360_turn/360 


#몇도가 비틀어지면 회전을 시도하는지
min_go_ahead_angle=10

# 1. 이미지 로드 및 이진화
def load_and_binarize_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return binary_image

# 2. 맨 위와 맨 아래 줄에서 흰색 픽셀들의 무게 중심 구하기
def get_centroid_of_row(binary_image, row):
    white_pixels = np.where(binary_image[row] == 255)[0]
    if len(white_pixels) == 0:
        return None
    centroid = np.mean(white_pixels)
    return int(centroid)

def get_middle_of_row(binary_image,row_index):
    height, width = binary_image.shape[:2]
    
    if row_index >= height:
        raise ValueError("행 번호가 이미지 높이보다 큽니다.")

    # 중심 열 인덱스 계산 (0부터 시작)
    center_col_index = width // 2

    # 중심 픽셀 인덱스 반환
    return  center_col_index

# 3. 두 픽셀을 연결하는 직선 그리기
def draw_line(image, start_point, end_point):
    color = (0, 0, 255)  # 빨간색
    thickness = 2
    cv2.line(image, start_point, end_point, color, thickness)

# 4. 직선이 세로선과 이루는 각도 계산
def calculate_angle(start_point, end_point):
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)
    # 세로선과의 각도이므로 수직선(90도)에서 빼줌
    vertical_angle = 90 - abs(angle_degrees)
    return vertical_angle

def masked_frame(frame):
    
    # HSV기준으로 frame을 마스킹해서 넘파이 
    pass

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '172.30.1.76'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9999
message = b'Hello'

client_socket.sendto(message,(host_ip,port))
fps,st,frames_to_count,cnt = (0,0,20,0)

def process_frame(frame):
    if frame is None:
        return "none"

    crop_img = frame[45:frame.shape[0], 0:frame.shape[1]]
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
        
    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])
        
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=2)
    binary_image = cv2.dilate(mask, None, iterations=2)
    cv2.imshow('mask', binary_image)

  
    
    # 위쪽과 아래쪽 줄의 인덱스
    top_row = 0
    bottom_row = binary_image.shape[0] - 1
    
    # 각 줄에서 흰색 픽셀의 무게 중심 찾기
    top_centroid = get_centroid_of_row(binary_image, top_row)
    bottom_centroid = get_centroid_of_row(binary_image, bottom_row)
    
    bottom_middle=get_middle_of_row(binary_image,bottom_row)
    top_middle=get_middle_of_row(binary_image,top_row)
    
    #무게 중심이 중앙으로부터 오른쪽에 있으면 +, 왼쪽에 있으면 -임!!
    try:
        # TypeError가 발생할 수 있는 코드
        bias_from_center_bottom=-bottom_middle+bottom_centroid
        bias_from_center_top=-top_middle+top_centroid

    except TypeError:
        print("asd")
        pass
    
    if top_centroid is None or bottom_centroid is None: # 이 경우에 대해서도 하기는 해야됨!!!
        print("흰색 픽셀이 부족하여 무게 중심을 계산할 수 없습니다.")
        return 'floor '
    
    # 두 점으로 이루는 직선 그리기
    start_point = (top_centroid, top_row)
    end_point = (bottom_centroid, bottom_row)
    
    # 원본 이미지에 직선 그리기
    image_with_line = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    draw_line(image_with_line, start_point, end_point)
    
    # 각도 계산
    angle = calculate_angle(start_point, end_point)
    
    
    
    # 결과 출력
    print(f"세로선과 이루는 각도: {angle:.2f}도")
    
    
    bias_from_center_bottom=-(bottom_middle-bottom_centroid)
    bias_from_center_top=-(top_middle-top_centroid)#얘는 혹시 몰라서 계산해놓음
    
    #결과 이미지 출력
    cv2.imshow('line',cv2.cvtColor(image_with_line, cv2.COLOR_BGR2RGB))
    
    
    if abs(angle)<min_go_ahead_angle: #라인이 세로선과 평행하게 놓여있음
        
        if abs(bias_from_center_bottom)<50:#라인이 프레임에서 중앙에 있음
            print(bias_from_center_bottom)
            return "go_ahead" #프로토콜 맞는지 확인!!!
        
        elif bias_from_center_bottom<0: # 라인이 프레임에서 왼쪽으로 치우침
            print(bias_from_center_bottom)
            return 'pan_right '+f'{abs(bias_from_center_bottom) * 0.07} '
        
        else: # 라인이 프레임에서 오른쪽으로 치우침
            print(bias_from_center_bottom)
            return 'pan_left '+f'{abs(bias_from_center_bottom) * 0.07} '
            
            
        
    
    elif angle>0:# 라인이 세로선으로부터 반시계 방향으로 돌아가있음 
        return "clockwise "+f"{time_degree_ratio * angle} " #시계방향으로 몇초 돌아야 하는지 리턴
    
    else: # 라인이 세로선으로부터 시계 방향으로 돌아가있음
        return "counter_clockwise "+f"{time_degree_ratio * angle} " #반시계방향으로 몇초 돌아야 하는지 리턴
    
while True:
    packet,_ = client_socket.recvfrom(BUFF_SIZE)
    start_time = time.time()
    data = base64.b64decode(packet,' /')
    npdata = np.frombuffer(data,dtype=np.uint8)
    frame = cv2.imdecode(npdata,1)
    if frame is None:
        print("탈출")
    # frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.imshow("RECEIVING VIDEO",frame)

    result = process_frame(frame)
    # print(frame)
    print(result)
    if result is not None:
        client_socket.sendto(result.encode('utf-8'),(host_ip,port))
    else:
        pass
    end_time = time.time()
    print(f"Time: {end_time - start_time:.2f} seconds")

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        client_socket.close()
        cv2.destroyAllWindows()
        break
    if cnt == frames_to_count:
        try:
            fps = round(frames_to_count/(time.time()-st))
            st=time.time()
            cnt=0
        except:
            pass
    cnt+=1
    