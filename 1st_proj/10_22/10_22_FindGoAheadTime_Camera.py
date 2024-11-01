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

    # 결과 이미지 출력
    cv2.imshow("Camera Frame with Line", frame)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 해제 및 모든 윈도우 닫기
cap.release()
cv2.destroyAllWindows()
