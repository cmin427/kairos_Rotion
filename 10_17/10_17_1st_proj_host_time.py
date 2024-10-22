import cv2, imutils, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '172.30.1.32'  # socket.gethostbyname(host_name)
print(host_ip)
port = 9999
message = b'Hello'

client_socket.sendto(message, (host_ip, port))
fps, st, frames_to_count, cnt = (0, 0, 20, 0)

# 마지막 감지 시간 초기화
last_detection_time = 0
detection_interval = 2  # 2초의 텀

def process_frame(frame):
    if frame is None:
        return "none"

    crop_img = frame[45:frame.shape[0], 0:frame.shape[1]]
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imshow('mask', mask)

    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
            cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
            cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)

            return cx  # cx 값을 반환하여 후속 처리에서 사용

    return None  # 노란색 선이 감지되지 않음

while True:
    packet, _ = client_socket.recvfrom(BUFF_SIZE)
    start_time = time.time()
    data = base64.b64decode(packet, ' /')
    npdata = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(npdata, 1)
    if frame is None:
        print("탈출")
    
    cv2.imshow("RECEIVING VIDEO", frame)

    cx = process_frame(frame)
    current_time = time.time()

    if cx is not None:
        # 2초의 텀을 두고 결과를 전송
        if current_time - last_detection_time >= detection_interval:
            if 30 <= cx <= 55:
                result = 'left'
            elif 80 <= cx <= 120:
                result = 'right'
            else:
                result = 'go'

            print(result)
            client_socket.sendto(result.encode('utf-8'), (host_ip, port))
            last_detection_time = current_time  # 마지막 감지 시간 업데이트
        else:
            print("Waiting for the next detection interval...")
    else:
        print("No yellow line detected.")

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
