import cv2
import os

# 카메라 열기
cap = cv2.VideoCapture(1)

# 'RedLight' 폴더 생성 (만약 없다면)
if not os.path.exists('RedLight'):
    os.makedirs('RedLight')

# 캡쳐 횟수 초기화
count = 0

while True:
    # 카메라에서 프레임 읽기
    ret, frame = cap.read()

    # 프레임 출력
    cv2.imshow('frame', frame)

    # 'z' 키를 누르면 이미지 저장
    if cv2.waitKey(1) == ord('z'):
        count += 1
        filename = 'img_{}.jpg'.format(count)
        filepath = os.path.join('RedLight', filename)
        cv2.imwrite(filepath, frame)
        print('캡쳐 완료! 현재 캡쳐 횟수:', count)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) == ord('q'):
        break

# 카메라 해제 및 모든 창 닫기
cap.release()
cv2.destroyAllWindows()