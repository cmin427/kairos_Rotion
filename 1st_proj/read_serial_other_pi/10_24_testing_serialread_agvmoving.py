#from softwareserial_original import softwareSerial
# from softwareserial import softwareSerial
from softwareserial2 import softwareSerial
import time
import cv2
import imutils
import socket
import numpy as np
import base64
import threading
from pymycobot.myagv import MyAgv
#softserial part start
swser = softwareSerial(txd_pin = 17, rxd_pin=27, baudrate=9600,new=" ",eol=" ")
buffer =""
#softserial part ends.


mc = MyAgv('/dev/ttyAMA2', 115200)

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

vid = cv2.VideoCapture(0)  # replace 'rocket.mp4' with 0 for webcam
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
                    mc.clockwise_rotation(3,0.1)
                    ed=time.time()
                    print("elapsed time:",ed-st)

                elif command == 'right':
                    st=time.time()
                    latest_command = 'right'
                    mc.counterclockwise_rotation(3,0.1)
                    ed=time.time()
                    print("elapsed time:",ed-st)

                elif command == 'floor':
                    if latest_command == 'left':
                        st=time.time()
                        mc.clockwise_rotation(3,0.1)
                        ed=time.time()
                        print("elapsed time(floor):",ed-st) 

                    elif latest_command == 'right':
                        st=time.time()
                        mc.counterclockwise_rotation(3,0.1)
                        ed=time.time()
                        print("elapsed time(floor):",ed-st)

                    else:
                        st=time.time()
                        mc.go_ahead(3,0.1)
                        ed=time.time()
                        print("elapsed time(floor):",ed-st)

                else:
                    st=time.time()
                    mc.go_ahead(3,0.1)
                    ed=time.time()
                    print("elapsed time:",ed-st)
                agv_command = None  # 명령어 처리 후 초기화
                # latest_command = None
            print(f"latest command: {latest_command}")

def signal_reading():
    global buffer
    counter = 0
    num = 1
    msg = swser.read()
    #swser.read()
    if msg:
        buffer += msg
        counter += 1
    
    if counter == 2:
        print(num , ". received:",buffer)
        num += 1
        buffer =""
        counter =0


# 스레드 생성
video_thread = threading.Thread(target=send_video_frames)
control_thread = threading.Thread(target=control_agv)
command_thread = threading.Thread(target=process_agv_commands)
signal_thread = threading.Thread(target=signal_reading)

# 스레드 시작
video_thread.start()
control_thread.start()
command_thread.start()
signal_thread.start()

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
signal_thread.join()


