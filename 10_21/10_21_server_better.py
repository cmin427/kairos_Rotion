# server
import cv2
import imutils
import socket
import numpy as np
import time
import base64
import threading
from pymycobot.myagv import MyAgv

class customAgv(MyAgv):
    def __basic_move_control(self, *genre, timeout = 5):
        t = time.time()
        self.__movement = True
        while time.time() - t < timeout and self.__movement is True:
            self._mesg(*genre)
            time.sleep(0.1)

    def go_ahead_custom(self, speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128 + speed, 128, 128, timeout=timeout)

    def pan_left_custom(self,speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("pan_right_speed must be between 1 and 127")
        self.__basic_move_control(128, 128 + speed, 128, timeout=timeout)
        
    def pan_right_custom(self,speed: int, timeout: int = 5):
        if not (0 < speed < 128):
            raise ValueError("pan_right_speed must be between 1 and 127")
        self.__basic_move_control(128, 128 - speed, 128, timeout=timeout)
        
    def clockwise_rotation_custom(self, speed: int, timeout=5):
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 - speed, timeout=timeout)

    def counterclockwise_rotation_custom(self, speed: int, timeout=5):
        if speed < 1 or speed > 127:
            raise ValueError("speed must be between 1 and 127")
        self.__basic_move_control(128, 128, 128 + speed, timeout=timeout)

mc=customAgv('/dev/ttyAMA2',115200)

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '172.30.1.30'  # socket.gethostbyname(host_name)
print(host_ip)
port = 9999
socket_address = (host_ip, port)
server_socket.bind(socket_address)
print('Listening at:', socket_address)

vid = cv2.VideoCapture(2)  # replace 'rocket.mp4' with 0 for webcam
fps, st, frames_to_count, cnt = (0, 0, 20, 0)

client_addr = None  # 클라이언트 주소 초기화
agv_command = None  # AGV 명령어 초기화
latest_command = "start" # 이전 명령어 초기화
command_lock = threading.Lock()  # 명령어 처리용 락

def send_video_frames():
    global client_addr, fps, st, cnt
    WIDTH = 160  # 너비를 160으로 설정
    HEIGHT = 120  # 높이를 120으로 설정
    while vid.isOpened():
        _, frame = vid.read()
        frame = imutils.resize(frame, width=WIDTH, height=HEIGHT)
        encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        message = base64.b64encode(buffer)

        if client_addr:  # 클라이언트 주소가 유효한 경우에만 전송
            try:
                server_socket.sendto(message, client_addr)
            except Exception as e:
                print(f"Error sending message: {e}")

            start_time = time.time()
            frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count / (time.time() - st))
                    st = time.time()
                    cnt = 0
                except:
                    pass
            cnt += 1

def control_agv():
    global client_addr, agv_command
    while True:
        try:
            server_socket.settimeout(0.1)  # 타임아웃 설정
            msg, addr = server_socket.recvfrom(BUFF_SIZE)
            client_addr = addr  # 클라이언트 주소 업데이트
            msg_decoded = msg.decode('utf-8')
            print(msg_decoded)

            with command_lock:
                agv_command = msg_decoded  # AGV 명령어 업데이트

        except socket.timeout:
            pass  # 타임아웃이 발생하면 무시하고 계속 진행

def process_agv_commands():
    global agv_command, st, latest_command
    while True:
        with command_lock:
            command = agv_command
            if command:
                if command == 'left':
                    st=time.time()
                    latest_command = 'left'
                    mc.clockwise_rotation_custom(1, 0.1)
                    ed=time.time()
                    # print("elapsed time:",ed-st)

                elif command == 'right':
                    st=time.time()
                    latest_command = 'right'
                    mc.counterclockwise_rotation_custom(1, 0.1)
                    ed=time.time()
                    # print("elapsed time:",ed-st)

                elif command == 'floor':
                    if latest_command == 'left':
                        st=time.time()
                        mc.clockwise_rotation_custom(1, 0.1)
                        ed=time.time()
                        # print("elapsed time(floor):",ed-st) 

                    elif latest_command == 'right':
                        st=time.time()
                        mc.counterclockwise_rotation_custom(1, 0.1)
                        ed=time.time()
                        # print("elapsed time(floor):",ed-st)

                    else:
                        st=time.time()
                        mc.go_ahead_custom(1, 0.1)
                        ed=time.time()
                        # print("elapsed time(floor):",ed-st)

                else:
                    st=time.time()
                    mc.go_ahead_custom(1, 0.1)
                    ed=time.time()
                    # print("elapsed time:",ed-st)
                agv_command = None  # 명령어 처리 후 초기화
                # latest_command = None
            # print(f"latest command: {latest_command}")

# 스레드 생성
video_thread = threading.Thread(target=send_video_frames)
control_thread = threading.Thread(target=control_agv)
command_thread = threading.Thread(target=process_agv_commands)

# 스레드 시작
video_thread.start()
control_thread.start()
command_thread.start()

# 메인 스레드에서 종료 대기
try:
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
except KeyboardInterrupt:
    pass

# 종료 처리
vid.release()
server_socket.close()
video_thread.join()
control_thread.join()
command_thread.join()