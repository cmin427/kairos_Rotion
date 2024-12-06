import cv2
import numpy as np
import cv2.aruco as aruco
import time
import threading
from pymycobot.myagv import MyAgv
import os
import re
import serial
import glob


mc = MyAgv('/dev/ttyAMA2',115200)
lock = threading.Lock()

ser = serial.Serial(
    port='/dev/ttyAMA3',  # Raspberry Pi의 UART 포트 설정
    baudrate=9600,  # 통신 속도 설정
    parity=serial.PARITY_NONE,  # 패리티 비트 없음
    stopbits=serial.STOPBITS_ONE,  # 스톱 비트 1개
    bytesize=serial.EIGHTBITS,  # 데이터 비트 크기 8비트
    timeout=2
    
)

frames_folder = r"/home/er/final_project/aruco"  # 저장된 프레임 폴더 경로

# ArUco 마커 초기화
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()

# 플래그 초기화 및 거리 설정
turn_direction = None  # 'left' 또는 'right'를 저장하는 변수

# 보정 행렬과 왜곡 계수를 불러옵니다.
camera_matrix = np.load(r"Image/camera_matrix.npy")
dist_coeffs = np.load(r"Image/dist_coeffs.npy")

# 마커의 실제 크기를 정확히 설정합니다 (예: 0.08미터 = 8cm).
marker_length = 0.0015  # 마커의 실제 크기 (미터 단위)


frame=None
serial_reading_thread_interrupt_flag=False
line_tracing_thread_interrupt_flag=True

def delete_all_files_in_directory(directory_path):
    try:
        # 디렉토리 내 모든 파일 검색
        files = glob.glob(os.path.join(directory_path, '*'))
        
        if not files:
            print(f"'{directory_path}' 폴더가 비어 있습니다.")
            return
        
        for file in files:
            try:
                os.remove(file)
                print(f"삭제 완료: {file}")
            except Exception as e:
                print(f"파일 삭제 실패: {file}, 에러: {e}")
        
        print("모든 파일이 삭제되었습니다.")
        
    except Exception as e:
        print(f"디렉토리 접근 실패: {directory_path}, 에러: {e}")


# ArUco 마커 탐지 함수
def detect_aruco_markers(frame):
    # detect_aruco_frame=frame[(frame.shape[0]//3)*2:,:]
    aruco_sight = frame[(frame.shape[0]//3)*2:,:] 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 그레이스케일 변환
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
    return corners, ids


def mask_by_yellow(frame):
    # print(frame.shape)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
    lower_yellow = np.array([88, 19, 31])
    upper_yellow = np.array([111, 255, 255])
        
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    cnt = 1
    
    # cv2.imwrite("/home/er/final_project/mask/mask" + f"{cnt}" + ".jpg", mask)
    cnt=+1
    
    return mask 
  



def frame_image_process(frame):
    # crop frame to 1/3 of height (from bottom) --> change this later
    roi=frame[(frame.shape[0]//3)*2:,:] 
    
    # make frame to binary image
    masked_roi=mask_by_yellow(roi)
    
    return masked_roi
                    


def get_centroid_of_row(binary_image, row):
    white_pixels = np.where(binary_image[row] == 255)[0]
    # print("wpx: ",len(white_pixels))
    if len(white_pixels) == 0:
        # print("no white pixel")
        return -1
    centroid = np.mean(white_pixels)
    return int(centroid)


def activate_motor(centroid,frame_width):

    frame_width_center=frame_width//2
    threshold=frame_width*0.16

    # print("relative cetntroid position:", centroid/frame_width)
    
    if abs(frame_width_center-centroid)<threshold:
        print("go ahead")
        mc.go_ahead(5,0.8)
        
        mc.stop()
      
    elif centroid < frame_width_center:
        print("counterclocksiwe turn")
        mc.counterclockwise_rotation(1,0.35)
   
        mc.stop()
       
    else:
        print("clockwise turn ")
        mc.clockwise_rotation(1,0.35)
    
        mc.stop()
        
    
def frame_image_process_in_agv(frame):
    row_in_interest=frame[(frame.shape[0]//5)*4]
    
    row_in_interest=row_in_interest[:,np.newaxis,:]
    # print("before tp ",row_in_interest.shape)

    row_in_interest = np.transpose(row_in_interest,(1,0,2))
    # print("after tp ",row_in_interest.shape)
  
    masked_row=mask_by_yellow(row_in_interest)
    
    # cv2.imwrite("/home/er/final_project/maksed/masked" + f"{0}" + ".jpg", masked_row)
    
    centroid_position=get_centroid_of_row(masked_row,0)
    
    # print("centroid_position ",centroid_position)
    return centroid_position
    
def frame_image_process_in_colum_left(frame):
    
    # 프레임 5분의 1 지점 왼쪽에 조건을 만족하는 픽셀이 열개 이상이면
    # LEFT_YELLOW_DETECTED_LOAD 리턴
    # 아니면 LEFT_NO_YELLOW_LOAD 리턴
    
    # 프레임의 5분의 1 지점에서 열 크롭 (3개의 열)
    column_index = int(frame.shape[1]*0.1)  // 10  # 5분의 1 지점
    num_columns_to_crop = 1  # 크롭할 열의 개수
    column_in_interest = frame[:, column_index:column_index + num_columns_to_crop]  # 열 크롭
    
    frame_resize = column_in_interest[310:480, :]  # 모든 x축, y축 310부터 480까지
    # 노란색 마스크 적용
    masked_column = mask_by_yellow(frame_resize)
    # cv2.imshow("left", masked_column)
    # print("왼쪽 픽셀 갯수", cv2.countNonZero(masked_column))
    # 노란색이 감지되었는지 확인
    if cv2.countNonZero(masked_column) > 10:  # 노란색 픽셀이 하나라도 감지되면
        return "LEFT_YELLOW_DETECTED_LOAD"
    else:
        return "LEFT_NO_YELLOW_LOAD"

def frame_image_process_in_column_right(frame):
    # 5분의 1 지점에서 3개의 열 크롭
    column_index_right = int(frame.shape[1] * 9.9) // 10  # 오른쪽 5분의 4 지점
    num_columns_to_crop = 1  # 크롭할 열의 개수


    # 오른쪽 관심 열 크롭
    right_column = frame[:, column_index_right:column_index_right + num_columns_to_crop]
    
    frame_resize = right_column[310:480, :]
    masked_right_column = mask_by_yellow(frame_resize)
    # cv2.imshow("right", masked_right_column)
    # print("오른쪽 픽셀 갯수", cv2.countNonZero(masked_right_column))
    # 노란색 감지 여부 확인
    if cv2.countNonZero(masked_right_column) > 10:
        return "RIGHT_YELLOW_DETECTED_LOAD"  # 노란색이 감지된 경우
    else:
        return "RIGHT_NO_YELLOW_LOAD"  # 노란색이 감지되지 않은 경우

def load_frames_and_process(folder_path):
    #과거 이미지 캡쳐 트레이스 백 해서 왼쪽, 오른쪽 5분의1 지점 열 확인하고 
    #노란색 픽셀 개수 체크 
    # 하나라도 걸리면 바로 오른쪽, 왼쪽 방향 리턴 
    
    # 파일 리스트 가져오기
    file_list = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.jpg')
    ]

    # 숫자(cnt)를 기준으로 파일 정렬
    def extract_cnt(file_name):
        match = re.search(r"aruco(\d+)\.jpg", file_name)
        return int(match.group(1)) if match else -1  # 숫자가 없으면 -1 반환

    sorted_files = sorted(file_list, key=extract_cnt, reverse=True)  # cnt 높은 순으로 정렬

    for file_path in sorted_files:
        # 프레임 로드
        frame = cv2.imread(file_path)
        if frame is None:
            print(f"파일 {file_path}을(를) 읽을 수 없습니다.")
            continue
        
        # 노란색 감지
        result_left = frame_image_process_in_colum_left(frame)
        result_right = frame_image_process_in_column_right(frame)
        
        if result_left == "LEFT_YELLOW_DETECTED_LOAD":
            # print(f"{file_path}: 왼쪽 노란색이 감지되었습니다!")
            return "LEFT_YELLOW_DETECTED"
        else:
            # print(f"{file_path}: 왼쪽 노란색이 감지되지 않았습니다.")
            pass
            
        if result_right == "RIGHT_YELLOW_DETECTED_LOAD":
            # print(f"{file_path}: 오른쪽 노란색이 감지되었습니다!")
            return "RIGHT_YELLOW_DETECTED"
        else:
            # print(f"{file_path}: 오른쪽 노란색이 감지되지 않았습니다.")
            pass
 
def aruco_command(turn_direction):
    
    # 비상명령어에 대해 비상 동작하기 
    
    if turn_direction == "LEFT":
        print("Turning left...")
        mc.counterclockwise_rotation(1, 3)
        
    elif turn_direction == "RIGHT":
        print("Turning right...")
        mc.clockwise_rotation(1, 3)
         
    # elif turn_direction == "GG":
    elif 'G' in turn_direction:
        print("Moving forward...")
        mc.go_ahead(4, 3)
    else:
        print("Unknown command:"+turn_direction)  

  


def camera_destroy(vid):
    try:
        vid.release()
    except:
        pass

def camera_capture_thread():
    global frame
    cap=cv2.VideoCapture(-1)
    while True:
        ret, frame = cap.read()
        if not ret :
            print("cant read frame")
            return None
        
        #cv2.imshow("captured",frame)

def capture_new_frame(frame):
    """
    새로운 프레임을 캡처하는 함수
    """
    # 카메라 또는 프레임 소스에서 새 프레임을 캡처
    new_frame = None
    try:
        # 새 프레임을 카메라 또는 동영상 스트림에서 읽음
        new_frame = frame  # 또는 사용 중인 캡처 방법에 따라 적절히 설정
    except Exception as e:
        print(f"Error capturing new frame: {e}")
    return new_frame


# 컨트롤러에서 다이렉트로 오는 커맨드 파싱 
def parse_direct_command(command):
    """
    명령어를 파싱하여 'C_' 뒤의 문자와 'T_' 뒤의 숫자를 구분하여 반환.
    명령어 형식: "C_<method>_T_<parameter>"
    """
    try:
        # 명령어를 '_'로 분리
        parts = command.split("_")
        if len(parts) != 4 or parts[0] != "C" or parts[2] != "T":
            print(f"유효하지 않은 명령어 형식: {command}")
            return None, None

        # 'C_' 뒤 문자 추출
        method_name = parts[1]  # 예: "goahead"

        # 'T_' 뒤 숫자 추출
        try:
            param_value = float(parts[3])  # 예: 0.1
        except ValueError:
            print(f"유효하지 않은 매개변수 값: {parts[3]}")
            return None, None

        # 결과 반환
        return method_name, param_value

    except Exception as e:
        print(f"명령 파싱 중 오류 발생: {e}")
        return None, None

def serial_wait_and_readline(ser):
    while ser.in_waiting<=0:
        time.sleep(0.1)
        
    return ser.readline().decode('utf-8').strip()

def serial_send_DONE(ser):
    ser.write(('DONE\n').encode('utf-8'))
    
def serial_send_ACK(ser):
    ser.write(('ACK\n').encode('utf-8'))

def execute_direct_command(mc,method,parameter):
    if method == 'goahead':
        mc.go_ahead(1, parameter)
    elif method == 'retreat':
        mc.retreat(1, parameter)
    elif method == 'clockwise':
        mc.clockwise_rotation(1, parameter)
    elif method == 'counterclockwise':
        mc.counterclockwise_rotation(1, parameter)
    elif method == 'panleft':
        mc.pan_left(1, parameter)
    elif method == 'panright':
        mc.pan_right(1, parameter)
    elif method =='restore':
        mc.restore()
    else:
        print("invalid direct command")
        mc.stop()
        mc.restore()

def stop_serial_reading_thread():
    global serial_reading_thread_interrupt_flag
    serial_reading_thread_interrupt_flag=True

def resume_serial_reading_thread():
    global serial_reading_thread_interrupt_flag
    serial_reading_thread_interrupt_flag=False
    
def resume_linetracing_thread():
    global line_tracing_thread_interrupt_flag
    line_tracing_thread_interrupt_flag=False
    
def stop_linetracing_thread():
    global line_tracing_thread_interrupt_flag
    line_tracing_thread_interrupt_flag=True
    
    
def thread_linetrace():

   # 라인트레이스 모드중에는 not line tracing interrupt flag 쪽이 반복적으로 실행됨
   # 현재 코드는 프레임 받아서, 일반적인 선일때는 라인트레이스 하고
   # 직각일때는 주어진 동작만큼 길게 수행하고 
   # 아루코보면 아루코라고 보냄 
   
    global serial_reading_thread_interrupt_flag
   
    while True:
        while not line_tracing_thread_interrupt_flag:
                    current_frame = frame
                    
                
                    """
                    들어온 이미지 순서대로 저장 (짧음)
                    """
                    try:
                        cv2.imwrite("/home/er/final_final_project/aruco/aruco" + f"{cnt}" + ".jpg", current_frame)
                        # print("image saved")
                        cnt += 1
                    except:
                        pass

                    if current_frame is None:
                        continue
                    
                    
                    """
                    아루코마커 탐지시 aruco라고 전송, 받고 동작 수행 (긺)
                    """
                    # 아루코 마커 탐지
                    corners, ids = detect_aruco_markers(current_frame)
                    
                    if ids is not None:
                        for i in range(len(ids)):  # 모든 감지된 아루코 마커 순회
                            marker_id = ids[i][0]  # 현재 아루코 마커 ID
                            print(f"Detected Aruco ID: {marker_id}")
                            
                            # 각 마커별 포즈 추정
                            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
                                corners[i], marker_length, camera_matrix, dist_coeffs
                            )

                        # 변환벡터 tvec의 크기를 계산하여 거리를 계산함
                        distance = np.linalg.norm(tvec)
                        
                        if distance < 0.02:
                            print("stop")
                            mc.stop()
                            
                            print("go_straight")
                            mc.go_ahead(4, 3.25)  # 직진
                            
                            lock.acquire()
                           
                            
                            ser.write(('ARUCO\n').encode('utf-8'))
                            print("STOP을 완료하였고 ARUCO가 전송됨")
                            
                            
                            
                            #시리얼 입력 대기 및 명령 처리
                            turn_direction =serial_wait_and_readline(ser)
                            print(f"received while aruco waiting: {turn_direction}")
                            
                            aruco_command(turn_direction)
                            mc.stop()
                            
                            lock.release()
                            
                            # 회전 후 새로운 프레임 캡처
                            new_frame = capture_new_frame(frame)  # 새로운 프레임을 캡처하는 함수
                            if new_frame is not None:
                                current_frame = new_frame  # 이전 프레임을 대체
                                
                                try:
                                    cv2.imwrite("/home/er/final_final_project/aruco" + f"{cnt}" + ".jpg", current_frame)
                                    # cv2.imwrite("/home/er/final_project/new_aruco/new_aruco" + f"{cnt}" + ".jpg", current_frame)
                                    
                                    # print("image saved")
                                    cnt += 1
                                except:
                                    pass
                            else:
                                print("Error: Unable to capture a new frame after rotation")
                                continue
                        else:
                            pass
                        
                        
                    """
                    일반적인 라인트레이싱 (짧음)
                    """
                    # 프레임의 2/3 지점에서 노란 선의 중심 인덱스를 구함
                    centroid_idx = frame_image_process_in_agv(current_frame)
                    if centroid_idx is None:
                        time.sleep(0.3)
                        mc.stop()
                        continue

                    # 중심값을 기반으로 모터 구동
                    activate_motor(centroid_idx, current_frame.shape[1])
                    
                    """
                    라인트레이싱할 라인 없을시, 코너 감지하고 일정한 동작 수행 (긺)
                    """
                    # 더 이상 라인트레이싱 할 노란색 선이 없음을 감지
                    if centroid_idx == -1:
                        result_yellow_line_column = load_frames_and_process(frames_folder)  # 이전에 찍은 frame들을 load 해와서 해당하는 열에 노란색 선이 있는지 확인
                        if result_yellow_line_column == "LEFT_YELLOW_DETECTED":
                            # print("왼쪽 노란색 column 발견")
                            mc.go_ahead(4, 3)  # 직진
                            mc.counterclockwise_rotation(1, 3)  # 90도 회전
                        
                        elif result_yellow_line_column == "RIGHT_YELLOW_DETECTED":
                            # print("오른쪽 노란색 column 발견")
                            mc.go_ahead(4, 3)  # 직진
                            mc.clockwise_rotation(1, 3)  # 90도 회전
                            
                        else:
                            pass
        while line_tracing_thread_interrupt_flag:
            pass
main_command=None
current_agv_mode='STOP'
flag_is_main_command_updated=False



def agv_main():
    
    global current_agv_mode,line_tracing_thread_interrupt_flag,flag_is_main_command_updated,serial_reading_thread_interrupt_flag
    
    

    def execute_linetrace_mode():
        global current_agv_mode
        
        
        resume_linetracing_thread()
        
        received=serial_wait_and_readline(ser)
        print("received while linetrace mode: "+received)
        
        if received=='STOP':
            stop_linetracing_thread()
            
            current_agv_mode='STOP'
            return
        
        
        
    
    def execute_direct_mode():
        global current_agv_mode
        while True:
            received=serial_wait_and_readline(ser)
            print("received while directmode: "+received)  
                                
                            
            if received=='LINETRACE':
                
                current_agv_mode='LINETRACE'
                serial_send_ACK(ser)
                break
            
            elif received=='STOP':
                
                current_agv_mode='STOP'
                serial_send_ACK(ser)
                break
            
            else:
                method, parameter = parse_direct_command(received)
                # AGV 동작 처리
                execute_direct_command(method,parameter)

                serial_send_DONE(ser) # 각 명령어에 대해 동작 완료 후 보고 전송 
                print(f"{method}를 완료하였고 DONE이 전송됨")
            
                
            
        pass
    
    def execute_stop_mode():
        
        # 모터를 멈추고 대기하면서 다음 모드가 들어오면 모드만 바꿔주고 컨트롤러에 DONE 전송
        
        global current_agv_mode
        mc.stop()
        next_mode=serial_wait_and_readline(ser) # 여기서 대기
        
        if next_mode in ['STOP','LINETRACE','DIRECT']:
            raise ValueError(f'stop 모드 중에는 linetrace, direct만 수신 가능, received:{next_mode}')
        
        current_agv_mode=next_mode
        serial_send_ACK(ser)
        
        
    # 이미지 파일 쌓인거 삭제 
    delete_all_files_in_directory(r'/home/er/final_final_project/aruco')
    
    while True:
        if current_agv_mode=='LINETRACE':
            execute_linetrace_mode()
    
        elif current_agv_mode=='DIRECT':
            execute_direct_mode()
            
        elif current_agv_mode=='STOP':
            execute_stop_mode()
            
            
   



if __name__ == "__main__":


    mc.stop()
    mc.restore()

    t1 = threading.Thread(target=camera_capture_thread)
    t2 = threading.Thread(target=agv_main)
    

    
    t1.start()
    t2.start()

   
    t1.join()
    t2.join()

    

    
    cv2.destroyAllWindows()