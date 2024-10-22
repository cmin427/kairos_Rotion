import cv2
import numpy as np

cap = cv2.VideoCapture(0)



while True:
    ret, frame = cap.read()

    # BGR to HSV 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    
    
    x, y = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)
    
 

    pixel = hsv[y, x]

    print("HSV:", pixel)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()