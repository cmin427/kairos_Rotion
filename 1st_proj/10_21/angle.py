import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

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

# 5. 전체 흐름 구현
def process_image(image_path):
    binary_image = load_and_binarize_image(image_path)
    
    # 위쪽과 아래쪽 줄의 인덱스
    top_row = 0
    bottom_row = binary_image.shape[0] - 1
    
    # 각 줄에서 흰색 픽셀의 무게 중심 찾기
    top_centroid = get_centroid_of_row(binary_image, top_row)
    bottom_centroid = get_centroid_of_row(binary_image, bottom_row)
    
    if top_centroid is None or bottom_centroid is None:
        print("흰색 픽셀이 부족하여 무게 중심을 계산할 수 없습니다.")
        return
    
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
    plt.imshow(cv2.cvtColor(image_with_line, cv2.COLOR_BGR2RGB))
    plt.title(f'Angle: {angle:.2f} degrees')
    plt.show()

# 이미지 처리 실행
image_path = 'path_to_your_image.png'  # 이미지 경로 설정
process_image(image_path)