import cv2
import time
import numpy as np
from pymycobot.myagv import MyAgv

# 카메라 초기화
cap = cv2.VideoCapture(2)  # 2는 세 번째 카메라를 의미합니다.

mc = MyAgv('/dev/ttyAMA2', 115200)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 비율 설정
near_ratio = 0.4  # 가까운 곳 비율
far_ratio = 0.6   # 먼 곳 비율

# 시간 측정 변수
start_time = None
end_time = None
measured_time = None
go_ahead = False  # AGV 동작 상태 변수
red_dot_drawn = False  # 빨간 점이 그려졌는지 여부

while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 프레임 크기
    height, width, _ = frame.shape

    # 가까운 곳과 먼 곳의 비율에 따라 선의 위치 계산
    near_y = int(height * near_ratio)
    far_y = int(height * (1 - far_ratio))

    # 선의 시작점과 끝점
    start_point = (0, near_y)  # 왼쪽에서 가까운 곳
    end_point = (width, far_y)  # 오른쪽에서 먼 곳

    # 빨간색 선 그리기
    color = (0, 0, 255)  # BGR 형식에서 빨간색
    thickness = 2
    cv2.line(frame, start_point, end_point, color, thickness)

    # 노란색 선 감지
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_yellow = (20, 100, 100)  # 노란색의 하한
    upper_yellow = (30, 255, 255)  # 노란색의 상한
    mask = cv2.inRange(hsv_frame, lower_yellow, upper_yellow)

    # 노란색 선이 감지되었는지 확인
    if cv2.countNonZero(mask) > 0 and not go_ahead:
        go_ahead = True  # AGV 동작 시작
        mc.go_ahead(1, 5)  # AGV 동작
        start_time = time.time()  # 시간 측정 시작
        red_dot_drawn = True  # 빨간 점을 그릴 준비

    # 빨간 점 그리기
    if red_dot_drawn:
        center_point = (width // 2, height // 2)  # 중앙 점
        cv2.circle(frame, center_point, 5, (0, 0, 255), -1)  # 빨간 점 그리기

    # 빨간색 선이 프레임 밖으로 나갔는지 확인
    if go_ahead and (near_y < 0 or far_y > height):
        end_time = time.time()  # 시간 측정 종료
        measured_time = end_time - start_time
        print(f"빨간색 선이 프레임 밖으로 나가는 데 걸린 시간: {measured_time:.2f}초")
        mc.stop()
        mc.restore()  # AGV 동작 중지
        break

    # 결과 이미지 출력
    cv2.imshow("Camera Frame with Line", frame)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        mc.stop()
        mc.restore()  # AGV 동작 중지
        break

# 카메라 해제 및 모든 윈도우 닫기
cap.release()
cv2.destroyAllWindows()
