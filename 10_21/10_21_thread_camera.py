import threading
import cv2

def camera1():
    cam1 = cv2.VideoCapture(-1)  # 첫 번째 카메라 (USB 카메라 또는 CSI 카메라)
    if not cam1.isOpened():
        print("Camera 1 could not be opened.")
        return

    while True:
        ret, frame1 = cam1.read()
        if ret:
            cv2.imshow('Camera 1', frame1)
        else:
            print("Failed to read frame from Camera 1.")
            break

        if cv2.waitKey(1) == ord('q'):
            break

    cam1.release()
    cv2.destroyWindow('Camera 1')

def camera2():
    cam2 = cv2.VideoCapture(-2)  # 두 번째 카메라 (USB 카메라 또는 CSI 카메라)
    if not cam2.isOpened():
        print("Camera 2 could not be opened.")
        return

    while True:
        ret, frame2 = cam2.read()
        if ret:
            cv2.imshow('Camera 2', frame2)
        else:
            print("Failed to read frame from Camera 2.")
            break

        if cv2.waitKey(1) == ord('q'):
            break

    cam2.release()
    cv2.destroyWindow('Camera 2')

# 스레드 생성
camera1_thread = threading.Thread(target=camera1)
camera2_thread = threading.Thread(target=camera2)

# 스레드 시작
camera1_thread.start()
camera2_thread.start()

# 스레드가 끝날 때까지 대기
camera1_thread.join()
camera2_thread.join()

cv2.destroyAllWindows()
