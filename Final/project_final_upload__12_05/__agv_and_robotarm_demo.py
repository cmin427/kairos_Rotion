import time
import threading
from robot_module.robotParts import AGV_PositionController, SocketManagerToKiosk,RobotArmController,CameraManager,ArucoDetector,SocketManagerToCobot
import sys
import time

"""
테스트 방식

아루코 마커 A2를 붙이고 그 위 정 중앙에 박스 놓기

agv는 초기 위치에서 정방향 보게 놓고 시작 

A2까지 가서 물건 집는 시늉 두번 하고 라인트레이싱 마저 하면 성공 

"""


class WareDragon:
    def __init__(self):
        
        self.stop_flag=False
        

        self.agv=AGV_PositionController()
        self.robotArm=RobotArmController()
        self.camera=CameraManager()
        print("init 완료")
        self.th_main=threading.Thread(target = self.thread_main)
        self.th_main.daemon=True
        self.th_main.start()

        print("main thread 시작")
        
    
    
            
    
    def thread_main(self):
  
        agv=self.agv
        robotArm=self.robotArm
        
       
        
        while True:
      
            
           
            agv.set_next_order([['A2',2]])
            
            
            
            while not agv.is_current_customer_order_complete():
                
                # 3. order list를 오름차순으로 정렬하고 다음 목표 선반 위치와 목표 물건 수량을 찾는다. 
                next_position,quantity=agv.find_next_target_position_and_quantity()
                print("3")
                
                # 4. 현재 위치와 방향을 고려하여 다음 목표 위치로 이동하도록 agv에 명령을 내린다. 
                if agv.dragon_position_current==next_position:
                    pass  
                else:
                    if agv.is_position_before(agv.dragon_position_current,next_position) and agv.dragon_direction_current=='BACKWARD':
                        agv.turn_half()
                self.line_trace_until(next_position) # 이녀석 매우 중요!!!!
                print("4")
                
                # 5. agv가 아루코마커에서 너무 벗어났을시, agv를 직접 조작해서 맞는 위치로 이동한다. 
                self.direct_adjust_to_exact_position(next_position)
                print("5")
                
                for i in range(quantity):
                    # 6. 로봇암을 움직여서 물체를 집고 바구니에 넣는다. 
                    robotArm.pick_target_goods()
                    print("6")
                
                # 7. 루프 처음으로 돌아가서 남은게 있는지 확인하고, 있으면 루프를 재시작한다.
                print("7")
            
            #8. 없다면 코봇으로 향한다. 
            if agv.dragon_direction_current=='BACKWARD':
                agv.turn_half()
            self.line_trace_until("X0")
            
            
            
            
            

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
        
        # robotArm.CameraCapturePos(RobotArmController.RIGHT)
        # camera.set_camera_mode(CameraManager.FRAME_CROP_MODE_POSITION_DETECT)
        agv.set_agv_mode_linetrace()
        
        while(not camera.is_aruco_detected(aruco_id_to_detect)):
            pass
        print("물건을 찾았음")
        agv.set_agv_mode_stop()
        
        
   
    # def direct_adjust_to_exact_position(self,next_position,target_distance=0.2):
    
    #     aruco_id=ArucoDetector.getArucoIDbyPosition(next_position)
    
    #     # AGV 및 카메라 인스턴스 가져오기
    #     agv = self.agv
    #     camera = self.camera

    #     agv.set_agv_mode_direct_controll()
    

    #     # PID 파라미터 초기화
    #     Kp_yaw, Ki_yaw, Kd_yaw = 0.07, 0.01, 0.01  # Yaw PID 계수
    #     Kp_bias, Ki_bias, Kd_bias = 0.03, 0.005, 0.01  # Bias PID 계수
    #     Kp_distance, Ki_distance, Kd_distance = 2.0, 0.01, 0  # Distance PID 계수
        
    #     previous_yaw_error, integral_yaw_error = 0, 0
    #     previous_bias_error, integral_bias_error = 0, 0
    #     previous_distance_error, integral_distance_error = 0, 0

    #     start_time = time.time()

    #     # ArUco 마커가 감지될 때까지 대기
    #     while not camera.is_aruco_detected(aruco_id):
    #         print("No ArUco marker detected")
    #         time.sleep(1)

    #     # 피드백 루프
    #     while True:
    #         current_time = time.time()
    #         dt = current_time - start_time
    #         start_time = current_time

    #         # 현재 ArUco 상태 값 읽기
    #         bias = camera.get_bias_of_aruco(aruco_id)
    #         yaw = camera.get_yaw_of_aruco_marker(aruco_id)
    #         distance = camera.get_distance_to_aruco(aruco_id)

    #         # 과거 ArUco 상태 값 읽기
    #         previous_bias = bias
    #         previous_yaw = yaw
    #         previous_distance = distance
            
    #         # ArUco 상태 편차
    #         diff_bias = abs(bias-previous_bias)
    #         diff_yaw = abs(yaw-previous_yaw)
    #         diff_distance = abs(distance-previous_distance)
            
    #         if diff_bias < 0.1 and diff_yaw < 0.1 and diff_distance < 0.1:
    #             agv.agv_direct_controll(f"C_restore_T_0")
            
    #         print(f"Bias: {bias}, Yaw: {yaw}, Distance: {distance}")

    #         # 오차 계산
    #         yaw_error = yaw
    #         bias_error = bias
    #         distance_error = distance - target_distance

    #         # PID 계산
    #         # Yaw PID
    #         integral_yaw_error += yaw_error * dt
    #         derivative_yaw_error = (yaw_error - previous_yaw_error) / dt
    #         pid_yaw = (Kp_yaw * yaw_error) + (Ki_yaw * integral_yaw_error) + (Kd_yaw * derivative_yaw_error)
    #         previous_yaw_error = yaw_error
    #         print("pid_yaw", pid_yaw)
            
            
    #         # Bias PID
    #         integral_bias_error += bias_error * dt
    #         derivative_bias_error = (bias_error - previous_bias_error) / dt
    #         pid_bias = (Kp_bias * bias_error) + (Ki_bias * integral_bias_error) + (Kd_bias * derivative_bias_error)
    #         previous_bias_error = bias_error
    #         print("pid_bias", pid_bias)


    #         # Distance PID
    #         integral_distance_error += distance_error * dt
    #         derivative_distance_error = (distance_error - previous_distance_error) / dt
    #         pid_distance = (Kp_distance * distance_error) + (Ki_distance * integral_distance_error) + (Kd_distance * derivative_distance_error)
    #         previous_distance_error = distance_error
    #         print("pid_distance", pid_distance)


    #         # PID 출력값 제한
    #         pid_yaw = max(min(pid_yaw, 0.15), -0.15)  # Yaw PID 출력 제한
    #         pid_bias = max(min(pid_bias, 0.05), -0.05)  # Bias PID 출력 제한
    #         # pid_distance = max(min(pid_distance, 1.0), -1.0)  # Distance PID 출력 제한
            
                    
    #         #회전 정렬
    #         is_yaw_set=False
    #         is_bias_set=False
    #         is_distance_set=False
            
    #         if abs(yaw)<5:
    #             is_yaw_set=True

    #         elif yaw<0: 
    #             agv.agv_direct_controll(f"C_counterclockwise_T_{abs(pid_yaw)}") 
                
    #         else:
    #             agv.agv_direct_controll(f"C_clockwise_T_{abs(pid_yaw)}")
                
                
            
    #         # 앞뒤 정렬 
    #         if abs(bias)<10:
    #             is_bias_set=True
    #         elif bias>0:
    #             agv.agv_direct_controll(f"C_goahead_T_{abs(pid_bias)}")
    #         else:
    #             agv.agv_direct_controll(f"C_retreat_T_{abs(pid_bias)}")
                
            
    #         #좌우 정렬
    #         if abs(distance-target_distance)<0.08:
    #             is_distance_set=True
    #         elif distance>target_distance:
    #             agv.agv_direct_controll(f"C_panright_T_{abs(pid_distance)}")
                
    #         else:
    #             agv.agv_direct_controll(f"C_panleft_T_{abs(pid_distance)}")
            

    #         if is_yaw_set and is_bias_set and is_distance_set:
    #             agv.set_agv_mode_stop()
    #             break
                
    def direct_adjust_to_exact_position(self,next_position,target_distance=0.25):
        
        aruco_id=ArucoDetector.getArucoIDbyPosition(next_position)
        
        # AGV 및 카메라 초기화
        agv = self.agv
        camera = self.camera
        
        
        #direct mode 설정 
        agv.set_agv_mode_direct_controll()
    
        
        aruco_id=ArucoDetector.getArucoIDbyPosition(next_position)
        
        # PID 파라미터 초기화
        Kp_yaw, Ki_yaw, Kd_yaw = 0.17, 0.015, 0.01  # Yaw PID 계수
        Kp_bias, Ki_bias, Kd_bias = 0.1, 0.005, 0.01  # Bias PID 계수
        Kp_distance, Ki_distance, Kd_distance = 4.5, 0.01, 0.01  # Distance PID 계수
        previous_yaw_error, integral_yaw_error = 0, 0
        previous_bias_error, integral_bias_error = 0, 0
        previous_distance_error, integral_distance_error = 0, 0
        start_time = time.time()
        
        # ArUco 마커가 감지될 때까지 대기
        while not camera.is_aruco_detected(aruco_id):
            print("No ArUco marker detected")
            time.sleep(1)
            
        # 피드백 루프
        while True:
            current_time = time.time()
            dt = current_time - start_time
            start_time = current_time
            
            # 현재 ArUco 상태 값 읽기
            bias = camera.get_bias_of_aruco(aruco_id)
            yaw = camera.get_yaw_of_aruco_marker(aruco_id)
            distance = camera.get_distance_to_aruco(aruco_id)
            
            # 과거 ArUco 상태 값 읽기
            previous_bias = bias
            previous_yaw = yaw
            previous_distance = distance
            
            # ArUco 상태 편차
            diff_bias = abs(bias-previous_bias)
            diff_yaw = abs(yaw-previous_yaw)
            diff_distance = abs(distance-previous_distance)
            if diff_bias < 0.1 and diff_yaw < 0.1 and diff_distance < 0.1:
                agv.agv_direct_controll(f"C_restore_T_0")
            # print(f"Bias: {bias}, Yaw: {yaw}, Distance: {distance}")
            print("bias", bias)
            print(f"Bias error: {-bias-109}, diffYaw: {yaw}, diffDistance: {0.25-distance}")
            
            # 오차 계산
            yaw_error = yaw
            bias_error = -bias-109
            distance_error = distance - target_distance
            
            # PID 계산
            # Yaw PID
            integral_yaw_error += yaw_error * dt
            derivative_yaw_error = (yaw_error - previous_yaw_error) / dt
            pid_yaw = (Kp_yaw * yaw_error) + (Ki_yaw * integral_yaw_error) + (Kd_yaw * derivative_yaw_error)
            previous_yaw_error = yaw_error
            # print("Kp_yaw", Kp_yaw * yaw_error)
            # print("Ki_yaw", Ki_yaw * yaw_error)
            # print("Kd_yaw", Kd_yaw * yaw_error)
            print("pid_yaw", pid_yaw)
            
            # Bias PID
            integral_bias_error += bias_error * dt
            derivative_bias_error = (bias_error - previous_bias_error) / dt
            pid_bias = (Kp_bias * bias_error) + (Ki_bias * integral_bias_error) + (Kd_bias * derivative_bias_error)
            previous_bias_error = bias_error
            print("pid_bias", pid_bias)
            
            # Distance PID
            integral_distance_error += distance_error * dt
            derivative_distance_error = (distance_error - previous_distance_error) / dt
            pid_distance = (Kp_distance * distance_error) + (Ki_distance * integral_distance_error) + (Kd_distance * derivative_distance_error)
            previous_distance_error = distance_error
            print("pid_distance", pid_distance)
            
            # PID 출력값 제한
            pid_yaw = max(min(pid_yaw, 0.37), -0.37)  # Yaw PID 출력 제한
            pid_bias = max(min(pid_bias, 0.23), -0.23)  # Bias PID 출력 제한    
            # pid_distance = max(min(pid_distance, 1.0), -1.0)  # Distance PID 출력 제한
            
            #회전 정렬
            is_yaw_set=False
            is_bias_set=False
            is_distance_set=False
            
            if abs(yaw)<7:
                is_yaw_set=True
            elif yaw<0:
                agv.agv_direct_controll(f"C_counterclockwise_T_{abs(pid_yaw)}")
            else:
                agv.agv_direct_controll(f"C_clockwise_T_{abs(pid_yaw)}")
                
            # 앞뒤 정렬
            if abs(-bias-109)<30:
                is_bias_set=True
            elif bias>-109:
                agv.agv_direct_controll(f"C_goahead_T_{abs(pid_bias)}")
            else:
                agv.agv_direct_controll(f"C_retreat_T_{abs(pid_bias)}")
                
            #좌우 정렬
            if abs(distance-target_distance)<0.08:
                is_distance_set=True
            elif distance>target_distance:
                agv.agv_direct_controll(f"C_panright_T_{abs(pid_distance)}")
            else:
                agv.agv_direct_controll(f"C_panleft_T_{abs(pid_distance)}")
            if is_yaw_set and is_bias_set and is_distance_set:
                agv.set_agv_mode_stop()
                break
        



if __name__=="__main__":
    
    # 창룡's 메인 스레드 시작
    changryong=WareDragon()
    
    # q 넣고 엔터 누르면 전부 종료. 
    # changryong.wait_for_stop_flag()