import cv2
import numpy as np
from pymycobot.myagv import MyAgv

cap = cv2.VideoCapture(1)
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 800, 600)

mc = MyAgv('/dev/ttyAMA2', 115200)

# 현재 상태를 저장하는 변수
current_direction = "FORWARD"

def process_frame(roi):
    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (0, 255, 0), 2)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 검은색 범위 조정
    lower_black = np.array([0, 0, 0], dtype=np.uint8)
    upper_black = np.array([180, 255, 50], dtype=np.uint8)
    black_mask = cv2.inRange(hsv, lower_black, upper_black)

    # 모폴로지 연산으로 노이즈 제거
    kernel = np.ones((5, 5), np.uint8)
    black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_CLOSE, kernel)
    black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) > 500:  # 면적 기준을 높임
            cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                center_line = width // 2
                # 방향을 반대로 변경
                if cx < center_line - 50:
                    return "RIGHT", black_mask
                elif cx > center_line + 50:
                    return "LEFT", black_mask
                else:
                    return "FORWARD", black_mask  # 중앙에 있을 때

    return None, black_mask

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    height, width, _ = frame.shape
    roi_height = int(height / 2)
    roi_top = height - roi_height
    roi = frame[roi_top:, :]

    result, black_mask = process_frame(roi)

    if result == "LEFT":
        mc.pan_left(1)
        current_direction = "LEFT"  # 현재 방향을 LEFT로 설정
        print('left')
    elif result == "RIGHT":
        mc.pan_right(1)
        current_direction = "RIGHT"  # 현재 방향을 RIGHT로 설정
        print('right')
    elif result == "FORWARD":
        mc.go_ahead(1)  # 중앙에 있을 때 직진
        current_direction = "FORWARD"  # 현재 방향을 FORWARD로 설정
        print('forward')
    else:
        # 선을 찾지 못했을 때의 처리
        if current_direction == "LEFT":
            mc.pan_left(1)  # LEFT 방향으로 계속 이동하는 대신 후진
            print('retreating from left')
        elif current_direction == "RIGHT":
            mc.pan_right(1)  # RIGHT 방향으로 계속 이동하는 대신 후진
            print('retreating from right')
        else:
            mc.retreat(1)  # 기본적으로 후진
            print('retreating')

    cv2.imshow("Frame", roi)
    # cv2.imshow("Black Mask", black_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
