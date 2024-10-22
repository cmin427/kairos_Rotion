# This is server code to send video frames over UDP
import cv2, imutils, socket
import numpy as np
import time
import base64
import select 
from pymycobot.myagv import MyAgv

mc = MyAgv('/dev/ttyAMA2', 115200)

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '172.30.1.100'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9999
socket_address = (host_ip,port)
server_socket.bind(socket_address)
print('Listening at:',socket_address)

vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
fps,st,frames_to_count,cnt = (0,0,20,0)

client_addr = None      # 클라이언트 주소 초기화

while True:
    msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    print('GOT connection from ',client_addr)
    print(msg.decode('utf-8'))

    WIDTH=400
    while(vid.isOpened()):
        _,frame = vid.read()
        frame = imutils.resize(frame,width=WIDTH)
        encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
        message = base64.b64encode(buffer)
        #readable, writeable, errors = select.select([server_socket,], [server_socket,], [], 5)
        server_socket.sendto(message,client_addr)
        start_time = time.time()
        frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        # cv2.imshow('TRANSMITTING VIDEO',frame)
        msg_decoded = ''

        # 클라이언트에서 추가 메시지 수신
        try:
            server_socket.settimeout(0.1)  # 타임아웃 설정
            msg, addr = server_socket.recvfrom(BUFF_SIZE)
            print(msg.decode('utf-8'))
            end_time = time.time()
            print(f"Time: {end_time - start_time:.2f} seconds")
        except socket.timeout:
            pass  # 타임아웃이 발생하면 무시하고 계속 진행
        
        #Agv control
        if msg_decoded == 'left':
            mc.clockwise_rotation(1)
        elif msg_decoded == 'right':
            mc.counterclockwise_rotation(1)
        else:
            mc.go_ahead(1)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            server_socket.close()
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st=time.time()
                cnt=0
            except:
                pass
        cnt+=1