import cv2
import numpy as np


# 블록 색상 판별하는 함수
def color_detect(frame):

    # 색상 별 마스크 영역
    mask_green = cv2.inRange(frame, (60,75,80), (100,255,255))      # green
    mask_green = np.repeat(mask_green[:,:,np.newaxis],3,-1)
    mask_red = cv2.inRange(frame, (0,200,200), (180,255,255))     # red
    mask_red = np.repeat(mask_red[:,:,np.newaxis],3,-1)
    mask_yellow = cv2.inRange(frame, (10,100,80), (30,255,255))     # yellow
    mask_yellow = np.repeat(mask_yellow[:,:,np.newaxis],3,-1)
    mask_purple = cv2.inRange(frame, (130,85,51), (150,255,255))     # purple
    mask_purple = np.repeat(mask_purple[:,:,np.newaxis],3,-1)

    # 마스크랑 겹치는 영역
    dst1 = cv2.bitwise_and(frame,mask_green)
    dst2 = cv2.bitwise_and(frame,mask_red)
    dst3 = cv2.bitwise_and(frame,mask_yellow)
    dst4 = cv2.bitwise_and(frame,mask_purple)

    green_sum = np.sum(dst1)
    red_sum = np.sum(dst2)
    yellow_sum = np.sum(dst3)
    purple_sum = np.sum(dst4)

    # 제일 큰 값으로 반환
    if max(green_sum, red_sum, yellow_sum, purple_sum) == green_sum:
        color= 'Green'
    elif max(green_sum, red_sum, yellow_sum, purple_sum) == red_sum:
        color= 'Red'
    elif max(green_sum, red_sum, yellow_sum, purple_sum) == yellow_sum:
        color= 'Yellow'
    else:
        color='Purple'

    if color == 'Red':
        lower = np.array([150,80,80]) 
        upper = np.array([180,255,255])
    elif color == 'Green':
        lower = np.array([60,75,80])
        upper = np.array([100,255,255]) 
    elif color == 'Yellow':
        lower = np.array([10,100,80])
        upper = np.array([30,255,255]) 
    else:
        lower = np.array([130,85,51])
        upper = np.array([150,255,255])

    frame = cv2.inRange(frame, lower, upper)
    return frame

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    frame_copy = frame
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masked = color_detect(frame_hsv)
    # print(color)
    # cv2.imshow('frame',masked)
    
    # height, width, _ = frame.shape
    # center_x = int(width/2)
    # center_y = int(height/2)
    # size = 300
    # roi_x, roi_y, roi_w, roi_h = center_x-size//2, center_y-size//2, 300, 300
    # roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    # cv2.rectangle(frame, (center_x-size//2, center_y-size//2), (center_x+size//2, center_y+size//2), (255,255,255), 3)

    # # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # # print(frame_gray.shape)
    # # _, thr = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)
    # # _, thr = cv2.threshold(thr, 0, 255, cv2.THRESH_BINARY_INV)

    
    median = cv2.medianBlur(masked, 15)
    # cv2.imshow("masked",median)
    contours, _ = cv2.findContours(median, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cont in contours:
        rect = cv2.minAreaRect(cont)
    try:
        print(int(rect[0][0]),int(rect[0][1]))
        cv2.circle(frame_copy, (int(rect[0][0]),int(rect[0][1])), 5, (255,0,0), -1)  

    except:
        pass
    cv2.circle(frame_copy, (301, 418), 5, (255, 0, 0), -1)
    #     # approx = cv2.approxPolyDP(cont, cv2.arcLength(cont,True)*0.02, True)
    #     # arcLength - 컨투어의 둘레 길이 계산해주는 함수. True -> 폐곡선
    #     # approxPolyDP - 컨투어 단순화 해주는 함수. epsilon -> 근사화 정확도.(컨투어와 근사된 다각형 사이의 최대거리)
    #     # vtc = len(approx)
    #     # if vtc==4:
    #     #     (x, y, w, h) = cv2.boundingRect(cont)
    #     #     pt1 = (x,y)
    #     #     pt2 = (x+w, y+h)
    #     #     # if roi_x<x<roi_x+roi_w and roi_y<y<roi_y+roi_h:
    #     #     cv2.rectangle(frame, pt1, pt2, (255,0,0), 2)
    # # cv2.circle(frame_copy, (int(rect[0][0]),int(rect[0][1])), 1, (255,0,0), -1)  
    # # median = cv2.medianBlur(frame,15)
    # # cv2.imshow('gray', thr)
    # cv2.drawContours(frame_copy, contours, -1, (0, 255, 0), 3)
    cv2.imshow('frame', frame_copy)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()