"""
정차 실험 방법 

agv하고 라즈베리파이하고 옆면에 부착한 카메라 필요

라즈베리파이하고 agv 연결 필요 

라즈베리파이에 robot_module 패키지 넣고 옆에서 이 코드 실행 

아루코 마커 보이기만 하도록 대충 agv 배치 

목표: 
1.get_bias_of_aruco(aruco_id) 해서 나오는 값이 매우 작은 값이어야함(카메라상에서 aruco가 중심임)
2.get_yaw_of_aruco_marker 해서 나오는 값이 매우 작은 값이어야 함 
3.get_distance_to_arucomarker 해서 나오는 값이 특정 값이어야 함 

"""


from robot_module.robotParts import AGV_PositionController,CameraManager
import time

def direct_adjust_to_exact_position(aruco_id):
    
    
    
    agv=AGV_PositionController()
    camera=CameraManager()
    
    
    
    agv.set_agv_mode_direct_controll()
    
    target_distance=0.2 # 미터 단위로 30cm 
    
    while(not camera.is_aruco_detected(aruco_id)):
            print("no aruco")
            time.sleep(1)
    
    constant_yaw_to_turn=0.05 # yaw=30도 일 때 한 1.5초 회전? 얘는 알아봐야 
    constant_bias_to_go_and_retreat= 0.005 # bias=200픽셀 일 때 한 0.5초 
    contant_distance_to_pan= 5 # dist차이 = 0.1일때 한 0.5초
    while True:
        
        bias=camera.get_bias_of_aruco(aruco_id)
        yaw=camera.get_yaw_of_aruco_marker(aruco_id)
        distance=camera.get_distance_to_aruco(aruco_id)
        
        print('bias:',bias)
        print('yaw:',yaw)
        print('distance:',distance)
        
        
        # # ver 1 한번에 많이 가는 명령어 내리기
        # if abs(bias)<10 and abs(yaw)<10 and abs(distance-target_distance)<0.05:
        #     break
        
        # else: 
        #     if yaw>0:
        #         agv.agv_direct_controll(f"C_counterclockwise_T_{yaw * constant_yaw_to_turn}") 
        #     elif yaw<0:
        #         agv.agv_direct_controll(f"C_clockwise_T_{yaw * constant_yaw_to_turn}") 
                
        #     if bias>0:
        #         agv.agv_direct_controll(f"C_retreat_T_{bias * constant_bias_to_go_and_retreat}")
        #     elif bias<0:
        #         agv.agv_direct_controll(f"C_goahead_T_{bias * constant_bias_to_go_and_retreat}")
                
        #     if distance>target_distance:
        #         agv.agv_direct_controll(f"C_panright_T_{abs(distance-target_distance)*contant_distance_to_pan}")
        #     elif distance<target_distance:
        #         agv.agv_direct_controll(f"C_panleft_T_{abs(distance-target_distance)*contant_distance_to_pan}")
                
                
            
            
        #ver 2 한번에 0.1초 * 세쌍 이거를 여러번 반복하기 
        
        #회전 정렬
        is_yaw_set=False
        is_bias_set=False
        is_distance_set=False
        
        if abs(yaw)<10:
            is_yaw_set=True

        elif yaw<0: 
            agv.agv_direct_controll(f"C_counterclockwise_T_0.1") 
            
        else:
            agv.agv_direct_controll(f"C_clockwise_T_0.1") 
        
        # 앞뒤 정렬 
        if abs(bias)<10:
            is_bias_set=True
        elif bias>0: 
            agv.agv_direct_controll(f"C_retreat_T_0.1")
        else:
            agv.agv_direct_controll(f"C_goahead_T_0.1")
            
        
        #좌우 정렬
        if abs(distance-target_distance)<0.05:
            is_distance_set=True
        elif distance>target_distance:
            agv.agv_direct_controll(f"C_panright_T_0.1")
            
        else:
            agv.agv_direct_controll(f"C_panleft_T_0.1")
        

        if is_yaw_set and is_bias_set and is_distance_set:
            agv.set_agv_mode_stop()
            break
        
direct_adjust_to_exact_position(0)