# This is client code to receive video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '172.30.1.32'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9999
message = b'Hello'

client_socket.sendto(message,(host_ip,port))
fps,st,frames_to_count,cnt = (0,0,20,0)

def process_frame(frame):
    if frame is None:
        return "none"

    # frame = cv2.flip(frame, -1)
    # cv2.imshow('normal', frame)

    crop_img = frame[45:frame.shape[0], 0:frame.shape[1]]
    # BGR에서 HSV로 변환
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
        
    # 노란색 범위 설정 (Hue: 20-30, Saturation: 100-255, Value: 100-255)
    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])
        
    # 노란색 마스크 생성
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
    # 노이즈 제거
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imshow('mask', mask)

    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2. moments(c)

        if M['m00'] != 0:  # 분모가 0이 아닐 때만 계산
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
                
            cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
            cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
                
            cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)

        if cx >= 30 and cx <= 55:
            print('right')
            return 'right'
            # left(1)
        elif cx >= 80 and cx <= 120:
            print('left')
            return 'left'
            # right(1)
        else:
            print('go')
            return 'go'


while True:
    # 버퍼를 비우기 위해 가능한 모든 패킷을 읽어옵니다.
    while True:
        try:
            packet, _ = client_socket.recvfrom(BUFF_SIZE)
            # 패킷을 처리할 수 있는 경우, 루프를 종료합니다.
            break
        except BlockingIOError:
            # 버퍼가 비어있으면 예외가 발생하므로 무시합니다.
            continue

    start_time = time.time()
    data = base64.b64decode(packet, ' /')
    npdata = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(npdata, 1)
    
    if frame is None:
        print("탈출")
        continue  # frame이 None인 경우 다음 루프를 진행합니다.

    cv2.imshow("RECEIVING VIDEO", frame)

    result = process_frame(frame)
    print(result)
    
    if result is not None:
        client_socket.sendto(result.encode('utf-8'), (host_ip, port))
    
    end_time = time.time()
    print(f"Time: {end_time - start_time:.2f} seconds")

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        client_socket.close()
        cv2.destroyAllWindows()
        break

    if cnt == frames_to_count:
        try:
            fps = round(frames_to_count / (time.time() - st))
            st = time.time()
            cnt = 0
        except:
            pass
    cnt += 1
