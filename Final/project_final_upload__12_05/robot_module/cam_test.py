import cv2

# 카메라 열기 (0은 기본 카메라)
cap = cv2.VideoCapture(-1)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    # 프레임 캡쳐
    ret, frame = cap.read()
    
    if not ret:
        print("프레임을 가져오지 못했습니다.")
        break

    # 프레임 표시
    cv2.imshow('Camera', frame)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()

