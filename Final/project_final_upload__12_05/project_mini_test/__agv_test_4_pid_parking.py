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


from robot_module.robotParts import AGV_PositionController, CameraManager
import time

def direct_adjust_to_exact_position(aruco_id):
    # AGV 및 카메라 초기화
    agv = AGV_PositionController()
    camera = CameraManager()

    agv.set_agv_mode_direct_controll()
    
    target_distance = 0.2  # 목표 거리: 0.2m (20cm)

    # PID 파라미터 초기화
    Kp_yaw, Ki_yaw, Kd_yaw = 0.07, 0.01, 0.01  # Yaw PID 계수
    Kp_bias, Ki_bias, Kd_bias = 0.03, 0.005, 0.01  # Bias PID 계수
    Kp_distance, Ki_distance, Kd_distance = 2.0, 0.01, 0  # Distance PID 계수
    
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
        
        print(f"Bias: {bias}, Yaw: {yaw}, Distance: {distance}")

        # 오차 계산
        yaw_error = yaw
        bias_error = bias
        distance_error = distance - target_distance

        # PID 계산
        # Yaw PID
        integral_yaw_error += yaw_error * dt
        derivative_yaw_error = (yaw_error - previous_yaw_error) / dt
        pid_yaw = (Kp_yaw * yaw_error) + (Ki_yaw * integral_yaw_error) + (Kd_yaw * derivative_yaw_error)
        previous_yaw_error = yaw_error
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
        pid_yaw = max(min(pid_yaw, 0.15), -0.15)  # Yaw PID 출력 제한
        pid_bias = max(min(pid_bias, 0.05), -0.05)  # Bias PID 출력 제한
        # pid_distance = max(min(pid_distance, 1.0), -1.0)  # Distance PID 출력 제한
        
                
        #회전 정렬
        is_yaw_set=False
        is_bias_set=False
        is_distance_set=False
        
        if abs(yaw)<5:
            is_yaw_set=True

        elif yaw<0: 
            agv.agv_direct_controll(f"C_counterclockwise_T_{abs(pid_yaw)}") 
            
        else:
            agv.agv_direct_controll(f"C_clockwise_T_{abs(pid_yaw)}")
            
            
        
        # 앞뒤 정렬 
        if abs(bias)<10:
            is_bias_set=True
        elif bias>0:
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

# 함수 호출
direct_adjust_to_exact_position(0)