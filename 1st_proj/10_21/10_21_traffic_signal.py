import cv2
import numpy as np

from ultralytics import YOLO

# model = YOLO('yolov8n.pt')
model = YOLO(r"C:\Users\aqsw6\Downloads\best (4).pt")

cap = cv2.VideoCapture(1)

while True:
    _, frame = cap.read()
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = model.predict(frame)

    annotated_frame = results[0].plot() # annotation이랑 box를 simple하게 모두 보이도록 하는 것

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

    cv2.imshow("Detection", annotated_frame)

cap.release()
cv2.destroyAllWindows()