import cv2
import numpy as np

# 초기값 설정
x = 320  # x좌표 초기값
y = 240  # y좌표 초기값

# 콜백 함수
def update_x(val):
    global x
    x = val

def update_y(val):
    global y
    y = val

# 윈도우 및 슬라이더 생성
cv2.namedWindow('Camera')
cv2.createTrackbar('X', 'Camera', x, 640, update_x)  # x좌표 슬라이더
cv2.createTrackbar('Y', 'Camera', y, 480, update_y)  # y좌표 슬라이더

# 카메라 열기
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    print(frame.shape)
    # 슬라이더에서 얻은 값을 사용하여 점 그리기
    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    cv2.imshow('Camera', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
