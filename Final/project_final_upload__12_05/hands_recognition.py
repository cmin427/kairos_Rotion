import cv2
import mediapipe as mp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

url = 'http://localhost:8501'   # streamlit app url
# chrome_service = Service('/usr/bin/chromedriver')

mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)     # 탐지할 손의 최대 수

cap = cv2.VideoCapture(0)

prev_landmarks = None        # 이전 프레임에서 위치 저장
cnt = 0

while True:
    ret, frame = cap.read()
    # print(ret)

    # 정사각형 그리기
    height, width, _ = frame.shape
    center_x = int(width/2)
    center_y = int(height/2)
    square_size = 300
    cv2.rectangle(frame, (center_x-square_size//2, center_y-square_size//2), (center_x+square_size//2, center_y+square_size//2), (255,255,255), 3)
    # cv2.line(frame, (center_x, center_y-square_size//2), (center_x, center_y+square_size//2), (255,255,255), 1, cv2.LINE_AA)

    # 프레임 처리
    frame = cv2.flip(frame,1)       # 좌우반전
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    result = hands.process(frame)       # 손 인식
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if result.multi_hand_landmarks is not None:
        for res in result.multi_hand_landmarks:     # 관절 별 좌표값
            # mp_drawing.draw_landmarks(frame, res, mp_hands.HAND_CONNECTIONS)
            current_third = res.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]   # 중지만 사용
            
            if prev_landmarks:
                prev_third = prev_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP] # 이전 프레임의 중지 좌표
                # 이전 프레임과 현재 프레임 x좌표값 비교
                if abs(current_third.x - prev_third.x) > 0.05:
                    cnt += 1        # 이전 프레임하고 비교해서 벗어나면 흔든거로 간주

            prev_landmarks = res     # 현재 프레임 -> 이전 프레임으로 저장
    
    if cnt >= 5:    # 손 흔든거로 인식하면
        print('open')
        cap.release()   # frame 중지
        cv2.destroyAllWindows()
        # driver = webdriver.Chrome(service=chrome_service)
        driver = webdriver.Chrome()
        driver.get(url)     # streamlit app 열기
        while True:     # app 닫히면 close 출력
            if not driver.window_handles:
                print('close')
                break
        cnt = 0
        cap = cv2.VideoCapture(0)   # frame 다시 켜기
        
    cv2.putText(frame, f'count: {cnt}', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)
    cv2.putText(frame, 'Wave if you need help!', (center_x-square_size//2-30, center_y+square_size//2+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (85,255,255), 2)
    cv2.imshow('hand',frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
