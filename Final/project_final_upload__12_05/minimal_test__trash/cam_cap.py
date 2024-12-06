import cv2

cap=cv2.VideoCapture(1)

while True:
    f,r=cap.read()
    cv2.imshow("f",f)
    
    if cv2.waitKey(0):
        break
   
cv2.destroyAllWindows() 
cap.release()
  
    


