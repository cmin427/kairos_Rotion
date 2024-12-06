import cv2
import pyzbar.pyzbar as pyzbar
import os


ID_file="pass_id.txt"

if not os.path.exists(ID_file):
    with open(ID_file, 'x') as f:
        f.write("")
else:
    with open(ID_file,"w") as f:
        f.write("")


cap=cv2.VideoCapture(0)
last_qr_msg=None


while True:
    ret,frame=cap.read()
    
    if not ret:
        pass
    
    cv2.imshow("cam",frame)
    
    qr_list=pyzbar.decode(frame)
    print("qr detected:",len(qr_list))
    if len(qr_list)==0:
        print("0 qr detected")
        last_qr_msg=None
        pass
    
    elif len(qr_list)>1:
        print("more than 1 qr detected")
        last_qr_msg=None
        pass
    
    else:
        qr_detected=qr_list[0]   
        current_qr_msg=qr_detected.data.decode('utf-8')
        
        if current_qr_msg != last_qr_msg:
            
            print("goods' information",current_qr_msg)
            with open(ID_file, "w") as f:
                f.write(current_qr_msg)
            print("file updated")
                
            last_qr_msg=current_qr_msg
            
            
    if cv2.waitKey(1) == 27:
        break
    
cap.release()
cv2.destroyAllWindows()

    

