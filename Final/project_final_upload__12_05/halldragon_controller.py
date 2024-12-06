import threading
from robot_module.robotParts import AGV_PositionController,CameraManager,ArucoDetector
import sys
import time

import RPi.GPIO as GPIO #RPi.GPIO 라이브러리를 GPIO로 사용
from time import sleep  #time 라이브러리의 sleep함수 사용


info_file = "info.txt"
stop_sign_file="done.txt"

# 파일 두개 내용 초기화 
with open(info_file, 'w') as f: 
    f.write("")
with open(stop_sign_file, 'w') as f:
    f.write("") 
    

class WareDragon:
    
    GOODS_PATH_INFO={'A':{"cam direction":'right',"forward":['GO'],"backward":['GO']},
                   'B':{"cam direction":'left',"forward":['RIGHT','LEFT'],"backward":['RIGHT','LEFT']},
                   'C':{"cam direction":'right',"forward":['RIGHT','LEFT'],"backward":['RIGHT','LEFT']},
                   'D':{"cam direction":'left',"forward":['RIGHT','GO'],"backward":['GO','LEFT']}}
    
    
    
    def __init__(self):
        self.servoPin          = 12   # 서보 핀
        self.SERVO_MAX_DUTY    = 12.5   # 서보의 최대(180도) 위치의 주기
        self.SERVO_MIN_DUTY    = 1.5    # 서보의 최소(0도) 위치의 주기

        GPIO.setmode(GPIO.BOARD)        # GPIO 설정
        GPIO.setup(self.servoPin, GPIO.OUT)  # 서보핀 출력으로 설정

        self.servo = GPIO.PWM(self.servoPin, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
        self.servo.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.

    
        self.stop_flag=False
        
        # self.camera=CameraManager()
        self.agv=AGV_PositionController()
        
        self.th_main=threading.Thread(self.th_main)
        self.th_main.daemon=True
        self.th_main.start()

    def wait_for_stop_flag(self): # q 누르면 각 파츠가 정지할 수 있게끔 main 마지막에서 호출하는 함수 
        
        user_input = input("종료하려면 'q'를 입력하세요: ").strip().lower()
    
        
        if user_input == 'q':
            print("종료 신호 감지. 창룡 모든 파트 정지.")
            
            self.stop_flag=True
            
            # agv에는 STOP 명령어를 보내고 중지한다. 
            self.agv.set_agv_mode_stop() #가능하면 시스템 종료 신호 받는거 만들기...
            self.agv.stop_flag=True
            print("agv 정지")
            
            
            # 카메라는 cap을 해제함 
            self.camera.stop_flag
            self.camera.thread_camera_capture.join()
            print("카메라 해제")
            
            sys.exit(0)
            
    def thread_main(self):
  
        agv=self.agv
        agv.set_agv_mode_stop()
        self.set_cam_direction("LEFT")
        
        while True:
            
            # 1. info file에 내용이 들어올때까지 대기한다. 
            while True:
                with open(info_file, 'r') as file:
                    # 파일 전체 내용 읽어오기
                    contents = file.read()
                    
                if contents != "":
                    print(contents)
                    break
                else:
                    time.sleep(1)
                    print("챗봇이 경로 설정줄때까지 대기중")
            
            # 2. info file 내용을 파싱해서 목표 선반에 대한 경로를 설정한다. 
            target_goods_info = contents.split('|')
            with open(info_file, 'w') as f: 
                f.write("")
            target_district=target_goods_info[1]
            target_subdistrict=target_goods_info[2]
            target_position=target_district+target_subdistrict # --> D2 
            
            self.cam=CameraManager() # 카메라 인스턴스 생성 
            
            target_aruco_id=ArucoDetector.getArucoIDbyPosition(target_position)
            
            target_dictionary=self.GOODS_PATH_INFO[target_district]
            
           
            cam_direction=target_dictionary['cam direction']
            forward=target_dictionary['forward']
            backward=target_dictionary['backward']
            
         
            # 3. 보고 멈춰야 하는 아루코마커가 있는 방향으로 카메라를 돌린다. 
            self.set_cam_direction(cam_direction) # 캠 달린 모터 제어하기 
            time.sleep(1)
            
            # 4. 라인트레이싱 시작 
            agv.set_agv_mode_linetrace()
            
            # 5. agv가 아루코 마커를 보았다고 신호를 보내면 알맞은 경로를 전송해준다. 이를 지정된 횟수만큼 ㅠㅠ 수행한다.
            for i in range(len(forward)):
                
                
                aruco_id_from_agv=agv.wait_for_agv_aruco_signal()
                direction=forward[i]
                agv.send_agv_direction_for_aruco(direction)
            
            # 6. 목표 상품이 있다고 생각되는 구역에 도착하면, 타겟 아루코마커를 보았을때 멈출 준비를 한다. 
            self.line_trace_until(target_position)
            
            # 7. 목표 상품에 도착
            print("매대에 도착")
            
            # 8. 반바퀴 돌아서 초기위치로 돌아갈 준비를 한다. 
            agv.turn_half()
            
            self.cam.close()

            # 9.chatbot에 매대 도착했다고 신호보냄 
            with open(stop_sign_file, 'w') as f:
                f.write("1")
            
            # 10. 운행이 종료되었다고 chatbot이 화면에 10초동안 표시함
            time.sleep(10)
            
            self.cam=CameraManager()
            
            # 11. 초기 위치로 돌아가기 위한 라인트레이싱 시작 
            agv.set_agv_mode_linetrace()
            
            # 12. 5번과 마찬가지. 
            for i in range(len(backward)):
                                
                aruco_id_from_agv=agv.wait_for_agv_aruco_signal()
                direction=backward[i]
                agv.send_agv_direction_for_aruco(direction)
            
            # 13. 초기 위치로 돌아가면 멈춘다. 
            self.line_trace_until('Z0')
            
            # 14. 반바퀴 돈다. 
            agv.turn_half()
            
            self.cam.close()
            # 15. chatbot한테 초기 상태로 돌아갔다고 신호를 보내준다. 
            
            with open(stop_sign_file, 'w') as f:
                f.write("0")
            
           
                
    def set_cam_direction(self,cam_direction):
        if cam_direction=="LEFT":
            self.__setServoPose(0)
            sleep(2)
        elif cam_direction=="RIGHT":
            self.__setServoPos(180)
            sleep(2)
        else:
            raise(ValueError("카메라 방향으로 잘못된 입력받음"))
            
    def __setServoPos(self,degree):
        # 각도는 180도를 넘을 수 없다.
        if degree > 180:
            degree = 180

        if degree<0:
            degree=0

        # 각도(degree)를 duty로 변경한다.
        duty = self.SERVO_MIN_DUTY+(degree*(self.SERVO_MAX_DUTY-self.SERVO_MIN_DUTY)/180.0)
        # duty 값 출력
        # print("Degree: {} to {}(Duty)".format(degree, duty))

        GPIO.setup(self.servoPin, GPIO.OUT)
        # 변경된 duty값을 서보 pwm에 적용
        self.servo.ChangeDutyCycle(duty)
        sleep(0.3)
        GPIO.setup(self.servoPin, GPIO.IN)     

    def line_trace_until(self,next_position): # 라인트레이싱을 하다가 next position에 해당하는 QR을 보면 정지한다
        agv=self.agv
        camera=self.camera

        """
        1. 로봇암을 카메라 찍는 위치로 잡는다 
        2. 카메라를 라인트레이싱 용 아루코 디텍팅 모드로 바꾼다. (프레임 중 일부에서만 아루코 마커 찾음)
        2-1 로그창 터질거 같으니까 램프로 디버깅 하는것도 괜찮을 거 같음 
        3. agv에 라인트레이싱 가능 신호를 보낸다. 
        3-1 만약에 안가면 디버깅을 어떻게 하지? 
        4. 카메라에 아루코마커가 잡히면 agv에 stop 신호를 보낸다. 
        
        """
        
        aruco_id_to_detect=ArucoDetector.getArucoIDbyPosition(next_position)
        
        
       
        agv.set_agv_mode_linetrace()
        
        while(not camera.is_aruco_detected(aruco_id_to_detect)):
            pass
            
        agv.set_agv_mode_stop()
        
        
   
            
    
    



if __name__=="__main__":
    
    # 창룡's 메인 스레드 시작
    changryong=WareDragon()
    
    # q 넣고 엔터 누르면 전부 종료. 
    changryong.wait_for_stop_flag()
    
    


