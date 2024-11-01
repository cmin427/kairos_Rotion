import cv2
import numpy as np
import math

cap = cv2.VideoCapture(1)  # 카메라 인덱스를 0으로 변경

# 카메라 해상도 설정 (예: 320x240)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# time_degree_ratio : clockwise를 속도 1로 실행시 1도를 몇초만에 도는지 
time_360_turn = 13
time_degree_ratio = time_360_turn / 360 

# 몇도가 비틀어지면 회전을 시도하는지
min_go_ahead_angle = 10

# 2. 맨 위와 맨 아래 줄에서 흰색 픽셀들의 무게 중심 구하기
def get_centroid_of_row(binary_image, row):
    white_pixels = np.where(binary_image[row] == 255)[0]
    if len(white_pixels) == 0:
        return None
    centroid = np.mean(white_pixels)
    return int(centroid)

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

def process_frame(frame):
    # 프레임을 10x10으로 리사이즈 (INTER_LINEAR 사용)
    small_img = cv2.resize(frame, (10, 10), interpolation=cv2.INTER_LINEAR)

    # HSV 변환
    hsv_small = cv2.cvtColor(small_img, cv2.COLOR_BGR2HSV)
        
    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])
        
    mask = cv2.inRange(hsv_small, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=1)  # 에로전 횟수 줄이기
    binary_image = cv2.dilate(mask, None, iterations=1)  # 다이레이션 횟수 줄이기

    # 10x10 이미지를 160x120으로 확대
    enlarged_img = cv2.resize(binary_image, (160, 120), interpolation=cv2.INTER_NEAREST)

    # 위쪽과 아래쪽 줄의 인덱스
    top_row = 0
    bottom_row = binary_image.shape[0] - 1
    
    # 각 줄에서 흰색 픽셀의 무게 중심 찾기
    top_centroid = get_centroid_of_row(binary_image, top_row)
    bottom_centroid = get_centroid_of_row(binary_image, bottom_row)
    
    if top_centroid is None or bottom_centroid is None:
        print("흰색 픽셀이 부족하여 무게 중심을 계산할 수 없습니다.")
        return None, None  # None 반환
    
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
    
    # 결과 이미지 출력
    return enlarged_img, small_img

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera error")
        break

    # 프레임 처리
    enlarged_img, small_img = process_frame(frame)

    cv2.imshow("RECEIVING VIDEO", frame)

    # enlarged_img가 None이 아닐 때만 imshow 호출
    if enlarged_img is not None:
        cv2.imshow("Enlarged Image", enlarged_img)  # 160x120으로 확대된 이미지 출력

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
