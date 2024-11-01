import cv2
import numpy as np

def main():
    camera = cv2.VideoCapture(-1)
    camera.set(3, 160)
    camera.set(4, 120)
    
    while camera.isOpened():
        ret, frame = camera.read()
        frame = cv2.flip(frame, -1)
        cv2.imshow('normal', frame)
        
        crop_img = frame[4*int(frame.shape[0]*0.2):frame.shape[0], 0:frame.shape[1]]
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
            
        lower_yellow = np.array([10, 150, 80])
        upper_yellow = np.array([40, 300, 250])
            
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cv2.imshow('mask', mask)

        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            
            if M['m00'] != 0:  # 분모가 0이 아닐 때만 계산
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
                cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
                
                cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)
                
                print(f"yellow line detected, cx: {cx}")  # X축 무게중심 출력
            else:
                cx = -1
                print(f"No yellow line detected1, cx: {cx}")  # 노란색 선이 감지되지 않음
        else:
            cx = -1
            print(f"No yellow line detected2, cx: {cx}")  # 노란색 선이 감지되지 않음
        
        if cv2.waitKey(1) == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
