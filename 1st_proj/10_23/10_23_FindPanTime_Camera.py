import cv2

# 카메라 초기화
cap = cv2.VideoCapture(1)  # 0은 기본 카메라를 의미합니다.

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 비율 설정 (반대로 변경)
near_ratio = 0.4  # 가까운 곳 비율
far_ratio = 0.6   # 먼 곳 비율

while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 프레임 크기
    height, width, _ = frame.shape

    # 빨간색 선 그리기
    color = (0, 0, 255)  # BGR 형식에서 빨간색
    thickness = 2
    start_point1 = (frame.shape[1]//3, frame.shape[1])
    end_point1 = (frame.shape[1]//3, 0)

    start_point2 = ((frame.shape[1]//3)*2, frame.shape[1])
    end_point2 = ((frame.shape[1]//3)*2, 0
                  )
    # roi = frame[:,frame.shape[1]//3 :(frame.shape[1]//3)*2] # 일단 roi를 가로로 가운데 3분의1만 보는걸로 해둠
    cv2.line(frame, start_point1, end_point1, color, thickness)
    cv2.line(frame, start_point2, end_point2, color, thickness)

    # 결과 이미지 출력
    cv2.imshow("Camera Frame with Line", frame)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 해제 및 모든 윈도우 닫기
cap.release()
cv2.destroyAllWindows()
