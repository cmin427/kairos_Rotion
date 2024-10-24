import numpy as np
import cv2
import cv2.aruco as aruco

def color_detect(frame):       # qr영역으로 crop된 이미지
    src_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 색상 별 마스크 영역
    mask_green = cv2.inRange(src_hsv, (60,75,80), (100,255,255))      # green
    mask_green = np.repeat(mask_green[:,:,np.newaxis],3,-1)
    mask_red = cv2.inRange(src_hsv, (150,80,80), (180,255,255))     # red
    mask_red = np.repeat(mask_red[:,:,np.newaxis],3,-1)
    mask_yellow = cv2.inRange(src_hsv, (10,100,80), (30,255,255))     # yellow
    mask_yellow = np.repeat(mask_yellow[:,:,np.newaxis],3,-1)

    # 마스크랑 겹치는 영역
    dst1 = cv2.bitwise_and(src_hsv,mask_green)
    dst2 = cv2.bitwise_and(src_hsv,mask_red)
    dst3 = cv2.bitwise_and(src_hsv,mask_yellow)

    green_sum = np.sum(dst1)
    red_sum = np.sum(dst2)
    yellow_sum = np.sum(dst3)

    # 제일 큰 값으로 반환
    if max(green_sum, red_sum, yellow_sum) == green_sum:
        return 'GreenLight'
    elif max(green_sum, red_sum, yellow_sum) == red_sum:
        return 'RedLight'
    else:
        return 'YellowLight'


# img = cv2.imread('traffic_signal_crop\RedLight\img_15.jpg')
# print(color_detect(img))

###


class QR_detector: 
    def __init__(self):
        self.camera_matrix = np.load(r"traffic_signal\Image\camera_matrix.npy")
        self.dist_coeffs = np.load(r"traffic_signal\Image\dist_coeffs.npy")
        self.marker_length=0.04
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters()
        
        self.corners=None
        self.ids=None
    
    def is_QR_detected(self):
        if self.ids is None:
            return False
        else:
            return True
        
    def detectQR(self,frame): #이미지나 프레임을 받아서 qr이 존재하면 관련 변수를 업데이트하고, 없으면 id 등
        #이미지를 그레이 스케일로 변경
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #마커 탐지
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.parameters
        )
        if ids is None:
            self.corners=None
            self.ids=None
        self.corners=corners
        self.ids=ids
        
        
        
    def distance_to_QR(self,frame):
        
        ids=self.ids
        corners=self.corners
        
        avg=-1
        
        if ids is not None:
            # 각 마커에 대해 루프를 돌면서 포즈를 추정합니다.
            sum=0
            for i in range(len(ids)):
                # 회전벡터(rvec), 변환벡터(tvec)
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
                    corners[i], self.marker_length, self.camera_matrix, self.dist_coeffs
                )
                # 변환벡터 tvec의 크기를 계산하여 거리를 계산함
                distance = np.linalg.norm(tvec)

                # 마커의 경계와 축을 그립니다.
                # aruco.drawDetectedMarkers(frame, corners)

                # 길이가 0.1인 축을 그림 (dist_coeffs: 왜곡 계수. 카메라 왜곡 보정용)
                # qcv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.1)

                # 거리를 화면에 출력합니다.
                # distance의 소수점 2자리까지 값 미터, 텍스트 위치, 텍스트 크기 1, 초록, 텍스트 선 두께 2
                # print(f"ID: {ids[i][0]} Distance: {distance:.3f} m")
                sum=sum+distance
            avg=sum/len(ids)
        return avg
    def crop_frame(self,frame):#이미지를 QR코드를 기준으로 crop함
        x_left, y_upper, x_right, y_lower = -1,-1,-1,-1
        #호정님 코드 이식
        marker_corners=self.corners
        marker_IDs=self.ids
        pt=[]
        if len(self.corners)==2:
            if(marker_IDs[0]==0): #프린트된 마커 쓸땐 2, 신호등 마커 쓸때는 0
                        
                pt.append(tuple(((marker_corners[1].reshape(4,2)).astype(int))[0]))
                pt.append(tuple(((marker_corners[0].reshape(4,2)).astype(int))[1]))
                pt.append(tuple(((marker_corners[0].reshape(4,2)).astype(int))[2]))
                pt.append(tuple(((marker_corners[1].reshape(4,2)).astype(int))[3]))
                
            else:
                
                pt.append(tuple(((marker_corners[0].reshape(4,2)).astype(int))[0]))
                pt.append(tuple(((marker_corners[1].reshape(4,2)).astype(int))[1]))
                pt.append(tuple(((marker_corners[1].reshape(4,2)).astype(int))[2]))
                pt.append(tuple(((marker_corners[0].reshape(4,2)).astype(int))[3]))
                
            # cv2.circle(frame, pt[0], 4, (0, 0, 255), 3)     # 3번 왼쪽 위
            # cv2.circle(frame, pt[1], 4, (0, 255, 0), 3)     # 2번 오른쪽 위
            # cv2.circle(frame, pt[2], 4, (255, 0, 255), 3)   # 2번 오른쪽 아래
            # cv2.circle(frame, pt[3], 4, (255, 0, 0), 3)     # 3번 왼쪽 아래
            
            
            y_upper = max(pt[0][1],pt[1][1])
            y_lower = min(pt[2][1],pt[3][1])
            x_left = min(pt[1][0],pt[2][0])
            x_right = max(pt[0][0],pt[3][0])
            # print(y_upper); print(y_lower); print(x_left); print(x_right)
            # cv2.rectangle(frame,(x_left, y_upper, abs(x_left-x_right), abs(y_upper-y_lower)),(255,0,0))
        else:
            print("no 2 QRq")
            return (x_left, y_upper, abs(x_left-x_right), abs(y_upper-y_lower))
        return (x_left, y_upper, abs(x_left-x_right), abs(y_upper-y_lower))
    
    

    def crop_img_with_QR(self,image,max_distance=0.25):
        self.detectQR(image)
        
        if(self.is_QR_detected()):#이미지 내에 QR이 존재할 경우 
            print('a')
            distance=self.distance_to_QR(image)
            if max_distance<distance:
                print('c')
                return None
            else:
                x,y,w,h=self.crop_frame(image)
                if x==-1:
                    return None
                cropped_img=image[y:y+h,x:x+w]
                print('d')
                print(cropped_img.shape)
                print(type(cropped_img))
                return cropped_img
        else:
            print('b')
            return None
        
        
        
detect=QR_detector()

def roi_crop(frame):
    img2=detect.crop_img_with_QR(frame,50)
    # print(detect.ids)
    if not detect.is_QR_detected():
        print("no QR")
        return
    
    return img2

###
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    img = roi_crop(frame)
    print(color_detect(img))