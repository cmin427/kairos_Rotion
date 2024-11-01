import cv2
import numpy as np
import time
from pymycobot.myagv import MyAgv

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

# 검은색 선을 감지하기 위한 함수
def detect_black_line(frame):
    # 색상 범위 설정 (노란색)
    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])

    crop_img = frame[45:frame.shape[0], 0:frame.shape[1]]
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
    
    # 색상 필터링
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imshow('mask', mask)

    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    return len(contours) > 0  # 검은색 선이 감지되면 True 반환

def main():
    cap = cv2.VideoCapture(-2)  # 카메라 초기화
    measuring = False
    start_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 검은색 선 감지
        if detect_black_line(frame):
            if not measuring:
                measuring = True
                start_time = time.time()
                mc.pan_right_custom(1, 0.1)  # 선이 감지되는 동안 이동

        else:
            if measuring:
                measuring = False
                elapsed_time = time.time() - start_time
                elapsed_minutes = elapsed_time / 60  # 분 단위로 변환
                print(f"Elapsed Time: {elapsed_minutes:.2f} minutes")
                mc.stop()  # 이동 중지
                mc.restore()  # 복원

        cv2.imshow("Camera Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 눌러 종료
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
