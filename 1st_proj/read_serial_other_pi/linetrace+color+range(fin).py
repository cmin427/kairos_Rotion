import cv2
# import imutils
import socket
import numpy as np
import time
import base64
import threading
from pymycobot.myagv import MyAgv
# import math
from softwareserial2 import softwareSerial
import string


mc = MyAgv('/dev/ttyAMA2',115200)
color_flag=None
distance_flag=None

ser = softwareSerial(txd_pin = 17, rxd_pin=27, baudrate=9600,new=" ",eol=" ")



def mask_by_yellow(frame):
    # print(frame.shape)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
    lower_yellow = np.array([10, 150, 80])
    upper_yellow = np.array([30, 280, 250])
        
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask 

            
            
def socket_initiate():
    
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = '172.30.1.100'#  socket.gethostbyname(host_name)
    print("set host ip to: ",host_ip)
    port = 9999
    socket_address = (host_ip,port)
    server_socket.bind(socket_address)
    print('Listening at:',socket_address)
    
    msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
    print('GOT connection from ',client_addr)
    print(msg.decode('utf-8'))
    
    return BUFF_SIZE,server_socket,client_addr
    
    
def camera_initiate():
    vid=cv2.VideoCapture(0)
    return vid


    
def frame_image_process(frame):
    
    
    # crop frame to 1/3 of height (from bottom) --> change this later
    roi=frame[(frame.shape[0]//3)*2:,:] 
    
    # make frame to binary image
    masked_roi=mask_by_yellow(roi)
    
    # 해상도 바꾸는 코드긴 한데 roi 좁게 잡으면 필요 없을듯 
    # cv2.resize(masked_roi,(200,200),interpolation=cv2.INTER_LINEAR)
    
    return masked_roi
                    
def send_frame_to_pc(frame,server_socket,client_addr):
    encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
    message = base64.b64encode(buffer)
    #readable, writeable, errors = select.select([server_socket,], [server_socket,], [], 5)
    server_socket.sendto(message,client_addr)
    
def receive_command_from_pc(server_socket,BUFF_SIZE):
    server_socket.settimeout(0.1)  # 타임아웃 설정
    msg, addr = server_socket.recvfrom(BUFF_SIZE)
    server_receiving=msg.decode('utf-8')
    print("server receiving: ",server_receiving)
    return msg 


# def activate_motor(command):
    # """
    # command can only be form of 
    
    # "go s1 t5" 
    # which means go_ahead(speed=1,time_out=5)
    
    # "clockwise s1 t5"
    
    # which means clockwise_rotation(speed=1,time_out=5)
    
    # "counterclockwise s1 t5"
    # which means counterclockwise_rotation(speed=1,time_out=5)
    
    
    # "no_line"
    # which means agv camera detected no line
    # """
    
    
    # words=command.split()
    # if words[0]=="no_line":
        
    #     mc.stop()
    #     print("agv stopped")
        
    # elif words[0]=="go":
    #     speed=words[1]
    #     timeout=words[2]
        
    #     mc.go_ahead(speed,timeout)
    #     print("agv go ahead")
        
    
    # elif words[0]=="clockwise":
    #     speed=words[1]
    #     timeout=words[2]
        
    #     mc.clockwise_rotation(speed,timeout)
    #     print("agv clockwise rotated")
        
    # elif words[0]=="counterclockwise":
    #     speed=words[1]
    #     timeout=words[2]
        
    #     mc.counterclockwise_rotation(speed,timeout)
    #     print("agv counterclockwise rotate")
    # else:
    #     print("unknown command received")
    #     print(command)
    
    
# distance_to_object=None
# traffic_sign=None

  
      
# def agv_main_loop():
    
#     vid=camera_initiate()
#     BUFF_SIZE,server_socket,client_addr=socket_initiate()
    
#     while True:
    
#         # 카메라로 사진 한장을 찍음
#         # capture 1 frame with agv camera
#         frame=camera_capture(vid)
        
#         # roi로 자르고 노란색 기준으로 마스킹함
#         # crop frame to roi and mask by yellow
#         mask_roi=frame_image_process(frame)
        
#         # 소켓으로 송출
#         # send to pc 
#         send_frame_to_pc(mask_roi,server_socket,client_addr)
    
#         # 소켓으로 주행용 제어값을 받음
#         # receive motor control command
#         msg_from_pc=receive_command_from_pc(server_socket,BUFF_SIZE)
        
#         while True:
#             if distance_to_object<10 or traffic_sign=='r' or traffic_sign=='y':
#                 time.sleep(0.5)
#             else:
#                 break
            
        
#         # 커맨드를 기준으로 모터를 구동함 
#         # activate motor by command
#         activate_motor(msg_from_pc)
        
        
        
#     camera_destroy()
#     socket_destroy()


def get_centroid_of_row(binary_image, row):
    white_pixels = np.where(binary_image[row] == 255)[0]
    # print("wpx: ",len(white_pixels))
    if len(white_pixels) == 0:
        print("no white pixel")
        return None
    centroid = np.mean(white_pixels)
    return int(centroid)

def activate_motor(centroid,frame_width):

    def _get_global_flags():
        current_distance_flag=distance_flag
        currnet_color_flag=color_flag
        return current_distance_flag,currnet_color_flag
    dist,colo=_get_global_flags()

    def _can_go(d,c):
        print("d",d)
        print("c",c)
        move_signal=True
        if d=='s':
            move_signal=False
            print("object detected in front of AGV")

        if c=='R' or c=='Y':
            move_signal=False
            print("stop traffic signal")
        return move_signal

    while dist is None:
        print("wait until sensor working")
        time.sleep(1)
        dist,colo=_get_global_flags()


    while not _can_go(dist,colo):
        time.sleep(3)
        dist,colo=_get_global_flags()

    print("can go")
    

    frame_width_center=frame_width//2
    threshold=frame_width*0.16

    print("relative cetntroid position:", centroid/frame_width)
    if abs(frame_width_center-centroid)<threshold:
        print("go ahead")
        mc.go_ahead(5,0.8)
        
        mc.stop()
      
    elif centroid < frame_width_center:
        print("counterclocksiwe turn")
        mc.counterclockwise_rotation(1,0.3)
   
        mc.stop()
       
    else:
        print("clockwise turn ")
        mc.clockwise_rotation(1,0.3)
    
        mc.stop()
        
    
def frame_image_process_in_agv(frame):
    
    row_in_interest=frame[(frame.shape[0]//5)*4]
    

    row_in_interest=row_in_interest[:,np.newaxis,:]
    # print("before tp ",row_in_interest.shape)

    
    row_in_interest = np.transpose(row_in_interest,(1,0,2))

    # print("after tp ",row_in_interest.shape)
    
  
    masked_row=mask_by_yellow(row_in_interest)
    
    centroid_position=get_centroid_of_row(masked_row,0)
    # print("centroid_position ",centroid_position)
    return centroid_position
    

"""
main loop not using socket
"""        


def camera_destroy(vid):
    try:
        vid.release()
    except:
        pass


frame=None

def camera_capture_thread():
    global frame
    cap=cv2.VideoCapture(-1)
    while True:
        ret, frame = cap.read()
        if not ret :
            print("cant read frame")
            return None
        #cv2.imshow("captured",frame)


def agv_main_loop():
    
    cnt=1
    while True:
    
        current_frame=frame 
        try:
            cv2.imwrite("/home/er/1st_project/kairos_Rotion-master/read_serial_other_pi/frame/frame"+f"{cnt}"+".jpg",current_frame)
            print("image saved")
            cnt=cnt+1
        except:
            pass
        if current_frame is None:
            continue
        
 
        # frame의 위에서 2/3 지점의 노란 선의 중심점의 인덱스를 구함
        # Finding the index of the center point of the yellow line at the 2/3 point from the top of the frame.
        centroid_idx=frame_image_process_in_agv(current_frame)
        if centroid_idx is None:
            time.sleep(0.3)
            mc.stop()
            continue
        
        # 커맨드를 기준으로 모터를 구동함 
        # activate motor by command
        activate_motor(centroid_idx,current_frame.shape[1])
        
        
        

    
    
"""
thread 2 read serial value from raspi 2 and change global variable 

in real time 

"""        
    
def serial_reading_thread():
    global distance_flag
    global color_flag
    
    while True:
        read_string=ser.read()

        
        
        print("serial mesg: ",read_string)
        # split read_string to sign0 and sign1
        try:
            idx_d=read_string.index('d')+1
            idx_c=read_string.index('c',idx_d)+1
            distance_flag=read_string[idx_d:idx_c-1]
            color_flag=read_string[idx_c:]
        except:
            continue                

        


            
            
if __name__ == "__main__":


    mc.stop()
    mc.restore()

    t2 = threading.Thread(target=agv_main_loop)
    t1 = threading.Thread(target=camera_capture_thread)
    t3 = threading.Thread(target=serial_reading_thread)

    t1.start()
    t2.start()
    t3.start()

   
    t1.join()
    t2.join()
    t3.join()
    
    agv_main_loop()

    
    cv2.destroyAllWindows()
    
   
    # socket_destroy() 