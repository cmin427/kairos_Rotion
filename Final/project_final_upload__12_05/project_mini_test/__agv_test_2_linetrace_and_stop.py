
#라인트레이싱 하다가 특정 구역에서 멈추는지 확인해보기.

import threading
from robot_module.robotParts import AGV_PositionController, SocketManagerToKiosk,RobotArmController,CameraManager 
import sys


class WareDragonLeg:
    def __init__(self):
        
        self.stop_flag=False
        
        
        self.agv=AGV_PositionController()
     
        self.camera=CameraManager()
        
      

        

    
   
            
        

    def line_trace_until(self,next_position):
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
        
        aruco_id_to_detect=CameraManager.getArucoIDbyPosition(next_position)
        
        # robotArm.CameraCapturePos(RobotArmController.RIGHT)
        
        camera.set_camera_mode(CameraManager.FRAME_CROP_MODE_POSITION_DETECT)
        agv.set_agv_mode_linetrace()
        
        while(not camera.is_aruco_detected(aruco_id_to_detect)):
            print("a")
            pass
            
        agv.set_agv_mode_stop()
        
            

leg=WareDragonLeg()

while True:
    
    user_input = input("구역 입력: A0, ").strip().lower()
    
        
    if user_input == 'q':
        leg.agv.set_agv_mode_stop() 
        leg.agv.stop_flag=True
        print("agv 정지")
        
        leg.camera.stop_flag
        leg.camera.thread_camera_capture.join()
        print("카메라 해제")
        break
    
    else:
        leg.line_trace_until(user_input)
        print(user_input,"에 도착")
        