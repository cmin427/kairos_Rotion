import cv2
import numpy as np
import math

# 이미지 파일 경로
image_path = r"C:\Users\aqsw6\Downloads\captured_image.jpg"  # 여기에 이미지 파일 경로를 입력하세요.

# 이미지 읽기
frame = cv2.imread(image_path)

if frame is None:
    print("이미지를 읽을 수 없습니다.")
else:
    # 프레임 해상도 설정 (예: 320x240)
    frame = cv2.resize(frame, (320, 240))

    # time_degree_ratio : clockwise를 속도 1로 실행시 1도를 몇초만에 도는지 
    time_360_turn = 13                
    time_degree_ratio = time_360_turn / 360 

    # 몇도가 비틀어지면 회전을 시도하는지
    min_go_ahead_angle = 10

    # 2. 흰색 픽셀들의 무게 중심 구하기
    def get_centroid_of_white_pixels(binary_image):
        white_pixels = np.where(binary_image == 255)
        if len(white_pixels[0]) == 0:
            return None
        centroid_x = np.mean(white_pixels[1])
        centroid_y = np.mean(white_pixels[0])
        return int(centroid_x), int(centroid_y)

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
        # 프레임을 HSV 변환
        small_frame = cv2.resize(frame, (200, 200), interpolation=cv2.INTER_LINEAR)
        hsv_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
        
        lower_yellow = np.array([10, 150, 80])
        upper_yellow = np.array([30, 280, 250])
        
        mask = cv2.inRange(hsv_small, lower_yellow, upper_yellow)
        mask = cv2.erode(mask, None, iterations=1)  # 에로전 횟수 줄이기
        binary_image = cv2.dilate(mask, None, iterations=1)  # 다이레이션 횟수 줄이기

        enlarged_frame = cv2.resize(small_frame, (320, 240), interpolation=cv2.INTER_NEAREST)

        # 전체 이미지에서 흰색 픽셀의 무게 중심 찾기
        centroid = get_centroid_of_white_pixels(binary_image)
        
        if centroid is None:
            print("흰색 픽셀이 부족하여 무게 중심을 계산할 수 없습니다.")
            return None, None, None  # None 반환
        
        # 무게 중심을 기준으로 직선 그리기
        start_point = (centroid[0], 0)  # 위쪽 끝
        end_point = (centroid[0], centroid[1])  # 무게 중심의 Y 좌표로 설정
        
        # 원본 이미지에 직선 그리기
        image_with_line = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        draw_line(image_with_line, start_point, end_point)
        
        # 각도 계산
        angle = calculate_angle(start_point, end_point)
        
        # 결과 출력
        print(f"세로선과 이루는 각도: {angle:.2f}도")
        
        # 결과 이미지 출력
        return binary_image, image_with_line, small_frame, enlarged_frame

    # 프레임 처리
    binary_img, image_with_line, small_frame, enlarged_frame = process_frame(frame)

    # 원본 크기로 복귀
    if binary_img is not None:
        # 원본 이미지와 함께 결과 출력
        cv2.imshow("Original Image", frame)
        cv2.imshow("Binary Image", binary_img)  # 이진화된 이미지 출력
        # cv2.imshow("Image with Line", image_with_line)  # 직선이 그려진 이미지 출력
        cv2.imshow("Small Frame", small_frame)  # 최소한의 크기로 줄인 이미지 출력
        cv2.imshow("enlarged_frame", enlarged_frame)

    cv2.waitKey(0)  # 키 입력 대기
    cv2.destroyAllWindows()
