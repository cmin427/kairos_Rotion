import cv2
import numpy as np
import os

# 폴더 경로 설정
led_on_folder = 'path_to_your_led_on_folder'
led_off_folder = 'path_to_your_led_off_folder'
output_folder = 'path_to_your_output_folder'  # 원하는 출력 폴더 이름 지정

# 출력 폴더가 없으면 생성
os.makedirs(output_folder, exist_ok=True)

# LED가 꺼진 폴더의 이미지 파일들로 V 채널 평균 계산
v_values = []

for filename in os.listdir(led_off_folder):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(led_off_folder, filename)
        image = cv2.imread(image_path)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv_image)

# V 채널의 평균 계산
avg_v = np.mean(v)

# LED가 켜진 폴더의 이미지 처리
for filename in os.listdir(led_on_folder):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(led_on_folder, filename)
        image = cv2.imread(image_path)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv_image)

        # V - avg_V 계산
        v_adjusted = v - avg_v

        # 결과를 300x100 크기로 리사이즈
        v_adjusted_resized = cv2.resize(v_adjusted, (300, 100))

        # 결과 저장
        output_path = os.path.join(output_folder, f'processed_{filename}')
        cv2.imwrite(output_path, v_adjusted_resized)

        print(f"{filename} 처리 완료: {output_path}")

print("모든 이미지 전처리가 완료되었습니다.")
