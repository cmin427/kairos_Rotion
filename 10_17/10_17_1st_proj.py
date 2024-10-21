import cv2
import numpy as np
from pymycobot.myagv import MyAgv
import time

cap = cv2.VideoCapture(1)
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 800, 600)

mc = MyAgv('/dev/ttyAMA2', 115200)

def process_frame(roi):
    cv2.line(roi, (width // 2, 0), (width // 2, roi_height), (0, 255, 0), 2)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_black = np.array([0, 0, 0], dtype=np.uint8)
    upper_black = np.array([180, 255, 50], dtype=np.uint8)  # 조정된 범위
    black_mask = cv2.inRange(hsv, lower_black, upper_black)
    black_mask = cv2.bitwise_not(black_mask)

    contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= 1:
        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) > 100:  # 면적 필터링
            cv2.drawContours(roi, [max_contour], -1, (0, 255, 0), 2)
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                center_line = width // 2
                # 방향을 반대로 변경
                if cx < center_line - 50:
                    return "RIGHT", black_mask  # 반대로 수정
                elif cx > center_line + 50:
                    return "LEFT", black_mask  # 반대로 수정

    return None, black_mask  # black_mask를 반환

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    height, width, _ = frame.shape
    roi_height = int(height / 2)  # 높이 조정
    roi_top = height - roi_height
    roi = frame[roi_top:, :]

    result, black_mask = process_frame(roi)  # black_mask를 받음

    if result == "LEFT":
        mc.pan_left(5)
        print('left')
    elif result == "RIGHT":
        mc.pan_right(5)
        print('right')
    else:
        mc.retreat(5)
        print('else')

    # 비디오 저장
    # out.write(roi)  # ROI를 비디오 파일에 저장

    cv2.imshow("Frame", roi)
    cv2.imshow("Black Mask", black_mask)  # 마스크 이미지 표시

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
# out.release()  # 비디오 파일 저장 종료
cv2.destroyAllWindows()
