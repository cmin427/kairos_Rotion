import cv2
import numpy as np

# 동영상 캡처 객체 생성
cap = cv2.VideoCapture(0)

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
    print("HSV:", pixel)
    cv2.circle(frame, (x,y), 10, (255,0,0), -1)

    # 프레임 출력
    cv2.imshow('frame', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) == ord('q'):
        break

# 캡처 해제 및 창 닫기
cap.release()
cv2.destroyAllWindows()