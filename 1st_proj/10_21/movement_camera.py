import cv2
import numpy as np
import time
from pymycobot.myagv import MyAgv

# 동영상 캡처 객체 생성
cap = cv2.VideoCapture(0)

class customAgv(MyAgv):
    def __basic_move_control(self, *genre, timeout=5):
        t = time.time()
        self.__movement = True
        while time.time() - t < timeout and self.__movement is True:
            self._mesg(*genre)
            time.sleep(0.1)

    def go_ahead_custom(self, speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128 + speed, 128, 128, timeout=timeout)

    def pan_left_custom(self, speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("pan_left_speed must be between 1 and 127")
        self.__basic_move_control(128, 128 + speed, 128, timeout=timeout)
        
    def pan_right_custom(self, speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("pan_right_speed must be between 1 and 127")
        self.__basic_move_control(128, 128 - speed, 128, timeout=timeout)
        
    def clockwise_rotation_custom(self, speed: int, timeout=5):
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 - speed, timeout=timeout)

    def counterclockwise_rotation_custom(self, speed: int, timeout=5):
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 + speed, timeout=timeout)

mc = customAgv('/dev/ttyAMA2', 115200)

# 특정 픽셀의 좌표 설정 (예: 화면 중앙)
while True:
    # 프레임 읽기
    ret, frame = cap.read()

    # BGR to HSV 변환
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    x, y = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
    
    # 특정 픽셀의 HSV 값 가져오기
    pixel = hsv[y, x]

    # HSV 값 출력
    cv2.circle(frame, (10,50), 10, (255,0,0), -1)

    # 프레임 출력
    cv2.imshow('frame', frame)


    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) == ord('q'):
        break

# 캡처 해제 및 창 닫기
cap.release()
cv2.destroyAllWindows()