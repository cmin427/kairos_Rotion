import serial
import socket
import time
import threading
import cv2 
import numpy as np
import json
import gc
import os






class SocketManagerToKiosk: #키오스크랑 소켓 통신을 하면서 픽업 리스트를 관리하는 클래스
    
    
        
    def __init__(self):
        
        # 한 고객의 주문 목록 리스트가 요소가됨, 리스트의 리스트
        self.stop_flag=False
        self.customers_order_list=[]
        self.socket_thread=self.socket_thread_init()
        
    # def __del__(self): # main 끝날때 인스턴스 소멸되면서 실행 # 작성 완 
    #     print("SocketManagerToKiosk's __del__")
    #     self.socket_thread.join()
        
    def have_order_to_deliver(self): # 키오스크에서 온 주문 목록이 남아있으면 true, 아니면 false # 작성 완
        if len(self.customers_order_list)>0:
            return False
        
        else:
            return True
        
    def socket_thread_init(self): # 소켓 스레드 시작시키고 스레드 객체 리턴. # 작성 완
        
        self.server_ip='172.30.1.57'
        self.port=9999
        
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        self.client_socket.connect((self.server_ip, self.port))
        
        print("connected to kiosk")
        
        server_th=threading.Thread(target=self.thread_ConnectedToServer)
        server_th.daemon=True # 메인 함수가 끝날때 알아서 끝남
        server_th.start()
        
        return server_th
 
    
    def thread_ConnectedToServer(self): # 키오스크로부터 데이터 있으면 받아서 order list에 추가 
        
        
        while not self.stop_flag:
        # 클라이언트로부터 메시지 수신
            data = self.client_socket.recv(1024*10) # 1024*10 바이트까지 수신
            if not data:
                print(">> Disconnected by server")
                break
            json_string = data.decode()
            deserialized_data = json.loads(json_string) # [[A0,2],[B2,1]]
            # print(f"키오스크 said : {deserialized_data}")
            data_ordered=[[element for element in sublist[::-1]] for sublist in deserialized_data]
            self. customers_order_list=(0,data_ordered) 
            # print(self.customers_order_list)
            
        self.client_socket.close()
        print("서버 소켓이 닫혔습니다")


    
    def get_next_order_data(self): # 가장 예전에 요청받은 order를 리스트에서 뽑아서 반환
        
        lst=self.customers_order_list
        
        if len(lst)==0:
            print("")
            return None
        
        next_customer_order=lst.pop()
        return next_customer_order


class SocketManagerToCobot:
    
    # 코봇 돌리는 pc의 포트로 설정하기 !!! 
    
    server_ip='172.30.1.57'
    server_port=9999
    
    def __init__(self):
        self.stop_flag=False
        self.socket_init()
        
        
        
    def socket_init(self): # 코봇의 포트와 연결하기 
    
        
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))  # 클라이언트의 포트 번호
        print("\n코봇과 소켓 통신으로 연결됨. 코봇의 포트: ",self.server_ip,".",self.server_port,'\n\n')
        
        return 
    
    def send_pickup_request_to_cobot_and_wait(self): # 코봇에게 바구니 집어가라고 요청하기 

        self.client_socket.sendall(bytes("PICK", "utf-8"))
        print("\n코봇에 'PICK' 전송\n")

        while True:
            
            message, self.addr = self.client_socket.recvfrom(1024)
            msg_decoded=message.decode()
            print("cobot said: ",msg_decoded)
            if msg_decoded == "DONE":
                print("클라이언트로부터 'DONE' 메시지를 받았습니다. 작업 완료.")
                break
    
    
    
class SerialUtils:
    @staticmethod
    def serial_write(ser,data,ACK=None,encoding_validity_function=None,send_multiple=False):
        
        # encoding validity function: data 정합성을 위한 인코딩을 할 것인지? 
        
        # ACK: 데이터를 보내고 ACK가 올때까지 기다릴 것인지? 
        
        # send_multiple: ACK가 안오면 재전송 할 것인지? 
        print("ack",ACK)
        ser.flushOutput()
        ser.flushInput()
        
        if encoding_validity_function is not None:
            data=encoding_validity_function(data) #  예시: checksum
            
        ser.write((data+'\n').encode('utf-8'))
        
        if ACK is not None:
            ser.flushOutput()
            ser.flushInput()
            while ser.in_waiting<=0:
                time.sleep(1)
   

            received=ser.readline().decode().strip()
            # print(received)
            # received = ser.readline()
            
            # print("received:",received)
            # print("in:",received.decode('utf-8').strip())
            while True:
                if received == ACK: 
                    print("received", ACK)
                    break
                else: 
                    print(f"ACK not matched, ACK:{ACK} received:{received}")
                    if send_multiple:
                        print("send again")
                        ser.write((data+'\n').encode('utf-8'))
                    while ser.in_waiting==0:
                        time.sleep(0.01)
                    received=ser.readline().decode().strip()
                    print(received)
         
            
                    
        return 
    
    def serial_read(ser,check_validity_function=None,ACK=None):
        while ser.inWating==0:
            time.sleep(0.1)
        data=ser.read(1024)
        
        return data 
    
    @staticmethod
    def wait_until_serial_wait(ser,data):
        while ser.inWating==0:
            time.sleep(0.1)
            
        input_serial=ser.read(1024)
        while True:
            if input_serial==data:
                break
            else:
                while ser.inWating==0:
                    time.sleep(0.1)
                input_serial=ser.read(1024) 
       
  
   
                
                
                
                
    @staticmethod
    def checkSum(text): # 상대 라즈베리파이에서 메시지 안깨졌음을 체크하기 위한 인코딩 #작성 완
        checksum=sum(text.encode()) % 256   
        return f"{text}|{checksum}"
    
    @staticmethod
    def checkSumValidity(text): # text를 chexkSum 함수 기준으로 인코딩하고 안깨졌으면 인코딩된 데이터 리턴, 깨졌으면 None
        
        index_of_bar=text.find('|')
        
        if index_of_bar == -1:
            return None
        
        data=text[:index_of_bar]
        checkSumStr=text[index_of_bar+1:]
        
        try:
            checkSum=int(checkSumStr)
        except ValueError:
            return None
        
        if sum(data.encode())% 256 != checkSum:
            return None
        
        return data
    
class AGV_PositionController: #agv 라즈베리파이랑 시리얼 통신을 하면서 구역 움직임과 미세조정?? 얘는 추가여따가 해야하는지.. 암튼 관리 
    
    AGV_MODE_STOP=0
    AGV_MODE_LINETRACE=1
    AGV_MODE_DIRECT_CONTROLL=2
    
    AGV_DIRECTION_FORWARD=0
    AGV_DIRECTION_BACKWARD=1
    
    def __init__(self):
        
        self.stop_flag=False

        self.dragon_position_current="Z0"
        self.dragon_direction_current=self.AGV_DIRECTION_FORWARD
        
        self.current_customer_order=[]   # ["A1","C2","B3"] 등 
        
        
        self.agv_mode=self.AGV_MODE_STOP
        
        self.id=0 #시리얼 통신 정밀하게 할때만 사용!!
        
        
        self.serial_communication_to_agv_initialize() # 시리얼 통신 담당 스레드 시작. 
  
    def turn_half(self): #얘도 timeout값 찾아야함!!!!!돌려서 반대 방향 라인 보일 정도기만 하면 됨
        self.set_agv_mode_direct_controll()
        self.agv_direct_controll("C_clockwise_T_6")
        self.set_agv_mode_stop()
             
    def is_position_before(self,posA,posB): # A가 B 이전에 있는가? 예: A2, B1 --> True
        A_alphabet=posA[0]
        A_index=posA[1:]
        B_alphabet=posB[0]
        B_index=posB[1:]
        
        if A_alphabet < B_alphabet:
            return True
        elif A_alphabet>B_alphabet:
            return False
        else:
            if A_index<B_index:
                return True
            else:
                return False
            
    def find_next_target_position_and_quantity(self): #현재 주문 목록을 오름차순으로 정리하고 맨 앞의 것을 리턴 #작성 완
        
        #입력: [[C1,3],[A0,1],[B2,2]] 출력: A0, 1
        
        self.current_customer_order.sort(key=lambda x: (x[0], x[1]))
        target=self.current_customer_order.pop(0)
        target_position,target_quantity=target[0],target[1]
        
        return target_position,target_quantity
        
            
        
        
    
    def is_current_customer_order_complete(self):
        if len(self.current_customer_order)==0:
            return True
        
        else:
            return False
    
    def set_next_order(self,order): # 현재 주문 목록을 order로 바꿈 # 작성 완
        
        self.current_customer_order=order
        
    
    def serial_communication_to_agv_initialize(self): # agv와 시리얼 통신을 위한 사전 확인
        self.ser = serial.Serial(
                port='/dev/ttyAMA4',
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2
                )
        time.sleep(2)  # Waiting for serial initialization

        
        self.ser.flushInput()
        self.ser.flushOutput()
        

        # agv 라즈베리파이에 최초로 연결 시도
        print("send first command to agv")
        self.set_agv_mode_stop()
        
        print("serial communication to agv is ready")
        
    

        
    def send_message_to_agv(self,text): 
    
        # 메시지를 보내고, DONE이 돌아올때까지 대기 
        SerialUtils.serial_write(self.ser,text,ACK="DONE")
        
    def wait_for_agv_aruco_signal(self):
        data=SerialUtils.serial_read(self.ser)
        return data
            
        
    def set_agv_mode_stop(self):
        
        self.send_message_to_agv("STOP")
        self.agv_mode=self.AGV_MODE_STOP
        
    def set_agv_mode_linetrace(self):
        
        self.send_message_to_agv("LINETRACE")
        self.agv_mode=self.AGV_MODE_LINETRACE
    
        
    def set_agv_mode_direct_controll(self):
        self.send_message_to_agv("DIRECT")
        self.agv_mode=self.AGV_MODE_DIRECT_CONTROLL
    
    def agv_direct_controll(self,command):
        if not self.agv_mode == self.AGV_MODE_DIRECT_CONTROLL:
            print("agv is not in direct controll mode!")
            return
        self.send_message_to_agv(command)
    
    def send_agv_direction_for_aruco(self,direction):
        self.send_message_to_agv(direction)
    
class ArucoDetector:
    ARUCO_POS_RELATE={"A1":100 , "A2":101, "A3":102, 
                        "B1":110, "B2":111,"B3":112,
                        "C1":120,"C2":121,"C3":122,
                        "Z0":200,"X0":201}
    
    
    def __init__(self): # 캘리브레이션 파일 집어넣어주기 ! 
        self.camera_matrix = np.load(r"robot_module/Image/camera_matrix.npy") 
        self.dist_coeffs = np.load(r"robot_module/Image/dist_coeffs.npy")
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        self.parameters = cv2.aruco.DetectorParameters()  
        self.marker_length=0.038 # 아루코 마커 크기 바꿔야 하면 얘 수정하기! 지금은 3.8cm
        
    
    @staticmethod
    def getArucoIDbyPosition(pos):
        if pos not in ArucoDetector.ARUCO_POS_RELATE:
            raise KeyError("invalid item position")
        return ArucoDetector.ARUCO_POS_RELATE[pos]
        
    
    def is_aruco_in_frame(self,frame, id):
       
        aruco_dict=self.aruco_dict 
        parameters=self.parameters 

          

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
                gray, aruco_dict, parameters=parameters)
    
        if ids is not None:
            for i in range(len(ids)):
                if ids[i][0] == id:
                    return True
                else:
                    return False
        else:
            return False
        
    def caculate_yaw_of_aruco(self,frame,id):
        camera_matrix=self.camera_matrix 
        dist_coeffs=self.dist_coeffs
        aruco_dict=self.aruco_dict 
        parameters=self.parameters 
        marker_length = self.marker_length

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters
        )

        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_length, camera_matrix, dist_coeffs
            )
            for i in range(len(ids)):
                if ids[i][0] == id:
                    rot_matrix, _ = cv2.Rodrigues(rvecs[i])
                    euler_angles = cv2.RQDecomp3x3(rot_matrix)[0]
                    return euler_angles[1]  # yaw
                else:
                    return None
        else:
            return None
        
        
        
    def caculate_center_of_aruco(self,frame,id):
   
        aruco_dict=self.aruco_dict 
        parameters=self.parameters 

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters
        )

        if ids is not None:
            for i in range(len(ids)):
                if ids[i][0] == id:
                    pt1 = corners[i][0][0]
                    pt2 = corners[i][0][1]
                    pt3 = corners[i][0][2]
                    pt4 = corners[i][0][3]
                    center_x = (pt1[0] + pt2[0] + pt3[0] + pt4[0]) / 4
                    center_y = (pt1[1] + pt2[1] + pt3[1] + pt4[1]) / 4
                    return center_x, center_y
                else:
                    return None
        else:
            None
    
    def get_distance_to_aruco(self,frame,id):
        camera_matrix=self.camera_matrix 
        dist_coeffs=self.dist_coeffs
        aruco_dict=self.aruco_dict 
        parameters=self.parameters 
        
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters
        )
        
        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_length, camera_matrix, dist_coeffs
            )
            
            
            for i in range(len(ids)):   
            
                if ids[i][0] == id:
                    distance= np.linalg.norm(tvecs[i])
                    return distance
                else:
                    return None
        else:
            return None
            
    
          
class CameraManager:
    FRAME_CROP_MODE_POSITION_DETECT=0
    FRAME_CROP_MODE_GRIP=1
    
    def __init__(self):
        
        self.stop_flag=False
        
        self.frame_crop_mode=self.FRAME_CROP_MODE_POSITION_DETECT
        self.current_frame=None
        self.frame_center=None
        self.cam_thread=self.cam_thread_init()
        
        self.aruco_detector=ArucoDetector()
        
    def close(self):
        print("close camera manager")
        self.stop_flag=True
        self.cam_thread.join()
        
        
        
        
        
    def cam_thread_init(self):
        self.folder_path="Images"
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            
        self.cap=cv2.VideoCapture(-1)
        
        print("컨트롤러에서 카메라 객체 생성")
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.frame_center=(width//2,height//2)
        print("frame center:",self.frame_center)
        th=threading.Thread(target=self.thread_camera_capture)
        
        th.start()
        return th
        
    
    def thread_camera_capture(self):
        
        while not self.stop_flag:
            ret,frame=self.cap.read()
            if not ret:
                continue
            self.current_frame=frame
            # cv2.imshow("hi",frame)
            cv2.imwrite(r"/home/rotion9/final_final_final_project/project_final/changyong/project_final/Images/img.jpg", frame)
            
        self.cap.release()
        print("카메라 객체 해제")
        


    def is_aruco_detected(self,id):
        frame=self.current_frame
        if frame is None:
            print("none")
            return False
        # mode=self.frame_crop_mode
        # frame=self.crop_frame(frame, mode)
        
        return self.aruco_detector.is_aruco_in_frame(frame,id)
    
    def get_yaw_of_aruco_marker(self,id):
        frame=self.current_frame
        yaw=self.aruco_detector.caculate_yaw_of_aruco(frame,id)
        
        if yaw is None:
            raise ValueError("aruco marker not detected")
        return yaw
    
    def get_bias_of_aruco(self,id):
        frame=self.current_frame
        x,y=self.aruco_detector.caculate_center_of_aruco(frame,id)
        
        return self.frame_center[0]-x
    
    def get_distance_to_aruco(self,id):
        frame=self.current_frame
        return self.aruco_detector.get_distance_to_aruco(frame,id)
        
        
    
class RobotArmController: 
    
    
    BASIC_POS=[140,150,180,70,180]


    
    def __init__(self):
        
        self.stop_flag=False
        
        self.current_angle=None
        self.id=0
        
        self.serial_communication_to_arm_initialize()
        

    
    def serial_communication_to_arm_initialize(self): # 아두이노와 시리얼 통신을 위한 사전 확인 바꿔야 할듯...?
        self.ser = serial.Serial(
                    port='/dev/ttyAMA3',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    
                    )
        
        time.sleep(2)
        self.ser.flushInput()
        self.ser.flushOutput()
        print("check if serial communication to robotarm is ready")
        
        
        # 아두이노에 요청 보내고 기다림 
        self.basic_pose()
        
        

        # 아두이노에서 올바른 응답이 온 경우 
        print("serial communication to robotarm is ready\n")
    
    def setGripperOpen(self):
        if self.current_angle[4]==180:
            return
        self.set_robot_arm_angle(finger=180)
        
    def setGripperClosed(self):
        # if self.current_angle[4]==0:
        #     return
        self.set_robot_arm_angle(finger=0)
    
    def basic_pose(self):
        self.set_robot_arm_angle(base=self.BASIC_POS[0],shoulder=self.BASIC_POS[1],elbow=self.BASIC_POS[2],wrist=self.BASIC_POS[3],finger=self.BASIC_POS[4])
        self.current_angle=self.BASIC_POS
        

    
    def set_robot_arm_angle(self,base=-1,shoulder=-1,elbow=-1,wrist=-1,finger=-1):
        abcd_message=f"a{base}b{shoulder}c{elbow}d{wrist}e{finger}f"
        self.__send_message_to_arm(abcd_message)
        self.current_angle=[base,shoulder,elbow,wrist,finger]
        
        
    def pick_target_goods(self):
        #1 학
        self.set_robot_arm_angle(base=140,shoulder=150,elbow=180,wrist=70,finger=180)
        time.sleep(1)
        print("1")
        
        # 1.1 집기 전 고개만 돌림
        self.set_robot_arm_angle(base=45,shoulder=150,elbow=180,wrist=70,finger=180)
        time.sleep(1)
        print("1.1")
        
        #2 중간
        self.set_robot_arm_angle(base=45,shoulder=70,elbow=130,wrist=70,finger=180)
        time.sleep(1)
        print("2")
        
        
        #3 집는 위치
        self.set_robot_arm_angle(base=45,shoulder=70,elbow=125,wrist=70,finger=180)
        time.sleep(1)
        print("3")
        
        #4 집기
        # self.setGripperClosed()
        # time.sleep(0.5)
        # self.setGripperClosed()
        # time.sleep(0.5)
        # self.setGripperClosed()
        self.set_robot_arm_angle(base=45,shoulder=70,elbow=125,wrist=70,finger=0)
        time.sleep(1)
        print("4")
        
        #5 중간 
        self.set_robot_arm_angle(base=45,shoulder=120,elbow=160,wrist=70,finger=0)
        time.sleep(1)
        print("5")
        
        #6 학
        self.set_robot_arm_angle(base=140,shoulder=150,elbow=180,wrist=70,finger=0)
        time.sleep(1)
        print("6")
        
        #7세밀조정
        self.set_robot_arm_angle(base=140,shoulder=110,elbow=160,wrist=5,finger=0)
        time.sleep(1)
        print("7")
        
        #8 그리퍼 열기 
        self.set_robot_arm_angle(base=140,shoulder=110,elbow=160,wrist=5,finger=180)
        time.sleep(1)
        print("8")
        
        #9 학
        self.basic_pose()
        time.sleep(1)
        print("9")
        
        
        
    def __send_message_to_arm(self,text):
        
        
        # 각도 명령어 checksum 인코딩해서 보내고 깨져서 가면 재전송 반복하기 
        SerialUtils.serial_write(self.ser,text,ACK='DONE',encoding_validity_function=SerialUtils.checkSum,send_multiple=True)  
        
       
      