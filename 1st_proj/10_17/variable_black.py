import cv2  # OpenCV를 사용하기 위해 import해줍니다.
import numpy as np  # 파이썬의 기본 모듈 중 하나인 numpy

def main():
    camera = cv2.VideoCapture(-1)  # 카메라를 비디오 입력으로 사용. -1은 기본설정이라는 뜻
    camera.set(3, 160)  # 띄울 동영상의 가로사이즈 160픽셀
    camera.set(4, 120)  # 띄울 동영상의 세로사이즈 120픽셀
    
    while camera.isOpened():  # 카메라가 Open되어 있다면,
        ret, frame = camera.read()  # 비디오의 한 프레임씩 읽습니다. ret값이 True, 실패하면 False, frame에 읽은 프레임이 나옴
        frame = cv2.flip(frame, -1)  # 카메라 이미지를 flip, 뒤집습니다. -1은 180도 뒤집는다
        cv2.imshow('normal', frame)  # 'normal'이라는 이름으로 영상을 출력
        
        crop_img = frame[60:120, 0:160]  # 세로는 60~120픽셀, 가로는 0~160픽셀로 crop(잘라냄)한다.
        
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)  # 이미지를 회색으로 변경
        
        blur = cv2.GaussianBlur(gray, (5, 5), 0)  # 가우시간 블러로 블러처리를 한다.
        
        # 검은색 선을 검출하기 위해 임계값을 조정합니다.
        ret, thresh1 = cv2.threshold(blur, 123, 255, cv2.THRESH_BINARY)  # 임계점 처리 (검은색을 흰색으로 변환)
        
        # 이미지를 압축해서 노이즈를 없앤다.
        mask = cv2.erode(thresh1, None, iterations=2)  
        mask = cv2.dilate(mask, None, iterations=2)
        cv2.imshow('mask', mask)
    
        # 이미지의 윤곽선을 검출
        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        # 윤곽선이 있다면, max(가장 큰 값)을 반환, 모멘트를 계산한다.
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
             
            # X축과 Y축의 무게중심을 구한다.
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # X축의 무게중심을 출력한다.
            cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
            cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
        
            cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)
            
            print(cx)  # 출력값을 print 한다.
        
        if cv2.waitKey(1) == ord('q'):  # q값을 누르면 종료
            break
    
    cv2.destroyAllWindows()  # 화면을 종료한다.

if __name__ == '__main__':
    main()